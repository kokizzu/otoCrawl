package main

import (
	"bufio"
	"encoding/json"
	"fmt"
	"io"
	"log"
	"math/rand"
	"net/http"
	"net/url"
	"os"
	"strconv"
	"time"

	"github.com/gocolly/colly"
)

const USER_AGENT_STR = "Mozilla/5.0 (X11; Linux x86_64; rv:60.0) Gecko/20100101 Firefox/81.0"

type Any interface{}

type Property struct {
	Id int `json:"id"`
}

type ResponseC struct {
	Status int `json:"status"`
	Data   struct {
		Items []Property `json:"items"`
	} `json:"data"`
}

type ResponseP struct {
	Status int `json:"status"`
	Data   Any `json:"data"`
}

func get(url string, ref string) ([]byte, error) {
	req, err := http.NewRequest(
		"GET",
		url,
		nil,
	)
	if err != nil {
		return nil, err
	}
	req.Header.Set("User-Agent", USER_AGENT_STR)
	req.Header.Set("Referer", ref)

	client := &http.Client{}
	res, err := client.Do(req)
	if err != nil {
		return nil, err
	}

	defer res.Body.Close()
	body, err := io.ReadAll(res.Body)
	if err != nil {
		return nil, err
	}

	return body, nil
}

func getProperty(prop_id int, ref string) (Any, error) {
	body, err := get(fmt.Sprintf("https://bff.591.com.tw/v1/community/price/detail?id=%d&split_park=1", prop_id), ref)

	var resp ResponseP
	err = json.Unmarshal(body, &resp)
	if err != nil {
		return nil, err
	}

	return resp.Data, nil
}

func getPropertyIdsFromComm(community_id string, ref string) ([]int, error) {
	fmt.Printf("Getting properties from community with id: %s\n", community_id)
	body, err := get(fmt.Sprintf("https://bff.591.com.tw/v1/community/price/lists?community_id=%s&split_park=1&page=1&page_size=1000&_source=0", community_id), ref)

	var resp ResponseC
	err = json.Unmarshal(body, &resp)
	if err != nil {
		return nil, err
	}

	var ids []int
	for _, prop := range resp.Data.Items {
		ids = append(ids, prop.Id)
	}

	return ids, nil
}

func writeProperty(property Any) error {
	f, err := os.OpenFile("props_tw.json", os.O_APPEND|os.O_WRONLY|os.O_CREATE, 0644)
	if err != nil {
		return err
	}
	defer f.Close()

	if bytes, err := json.Marshal(property); err == nil {
		f.Write(bytes)
		f.Write([]byte("\n"))
	}

	return nil
}

func main() {
	pageNum := 0
	completed := make(map[int]bool)
	f, err := os.OpenFile("property_id.txt", os.O_APPEND|os.O_RDWR|os.O_CREATE, 0644)
	if err != nil {
		log.Fatalln(err)
	}
	defer f.Close()

	scanner := bufio.NewScanner(f)
	for scanner.Scan() {
		if prop_id, err := strconv.Atoi(scanner.Text()); err == nil {
			completed[prop_id] = true
		}
	}

	stopRun := false
	c := colly.NewCollector(
		colly.AllowedDomains("market.591.com.tw"),
		colly.UserAgent(USER_AGENT_STR),
	)

	c.OnHTML(".left-container > a[href]", func(e *colly.HTMLElement) {
		link := e.Attr("href")

		u, err := url.Parse(link)
		if err != nil {
			log.Fatalln(err)
		}
		community_id := u.Path[1:]

		time.Sleep(time.Duration(rand.Intn(2000)+1000) * time.Millisecond)
		if ids, err := getPropertyIdsFromComm(community_id, fmt.Sprintf("https://market.591.com.tw/list?page=%d", pageNum)); err == nil {
			for _, prop_id := range ids {
				if !completed[prop_id] {
					time.Sleep(time.Duration(rand.Intn(1000)+100) * time.Millisecond)
					prop, err := getProperty(prop_id, fmt.Sprintf("https://market.591.com.tw/%s/price", community_id))
					if err == nil {
						if writeProperty(prop) == nil {
							completed[prop_id] = true
							f.WriteString(fmt.Sprintf("%d\n", prop_id))
						} else {
							fmt.Printf("Failed writing property with id: %d\n", prop_id)
						}
					} else {
						fmt.Printf("Failed getting property with id: %d\n", prop_id)
					}
				}
			}
		} else {
			fmt.Printf("Failed getting properties from community with id: %s\n", community_id)
		}
	})

	c.OnHTML(".left-container > .empty", func(e *colly.HTMLElement) {
		stopRun = true
	})

	c.OnRequest(func(r *colly.Request) {
		fmt.Println("\nVisiting", r.URL.String())
	})

	for !stopRun || pageNum < 10000 {
		pageNum++
		c.Visit(fmt.Sprintf("https://market.591.com.tw/list?page=%d", pageNum))
	}

	fmt.Println("Done!")
}
