#!/usr/bin/env ruby

require 'ap'
require 'nokogiri'
require 'active_support/core_ext/hash' # Hash.from_xml
require 'rubygems'
require 'excon'

DIR='shell/'
Dir.mkdir DIR unless Dir.exists? DIR

def urlS typ, page=1
    "https://shell-lmc-id.phoenix.earlweb.net/search?token=z8CVrwzZNUCU&language=id&q=#{typ}&page=#{page}&page_size=100&familygroup=Mobil"
end

def urlE href
    "https://shell-lmc-id.phoenix.earlweb.net#{href}?token=z8CVrwzZNUCU&language=id"
end

brands = %w(
    BMW
    Chevrolet
    Daihatsu
    Datsun
    Honda
    Hyundai
    Isuzu
    KIA
    Mazda
    Mercedes
    Mitsubishi
    Nissan
    Proton
    Suzuki
    Toyota
)

def getXmlSearch brand, page
    fname = "#{DIR}/#{brand}-#{page}.xml"
    ap "#{fname}"
    if File.exist? fname
        xml = File.read(fname)
    else 
        uri = urlS(brand,page)
        xml = Excon.get(uri).body
        File.open(fname, 'w') do |f| 
            f.write xml
        end
    end
    Hash.from_xml(xml)
end

def getXmlEqu href
    fname = "#{DIR}#{href.gsub '/','__'}.xml"
    ap "#{fname}"
    if File.exist? fname
        xml = File.read(fname)
    else 
        uri = urlE href
        xml = Excon.get(uri).body
        File.open(fname, 'w') do |f|
            f.write xml
        end
    end
    Hash.from_xml xml
end

File.open('shell.tsv', 'w') do |fr|
    brands.each do |brand|
        page = 1
        loop do 
            res = getXmlSearch brand, page
            page += 1
            el = res['response']['equipment_list']
            no_more = el['truncated'] != 'true'
            eqs = el['equipment']
            ap eqs.length
            eqs.each do |eq|
                res = getXmlEqu eq['href']
                product = res['response']['equipment']['application'][0]['product'] rescue res['response']['equipment']['application']['product'] rescue nil
                product = [{'name':'NULL1'},{'name':'NULL1'}] if product.nil?
                ap product # NOTE: tip tertentu misal izusu/truck2 tidak ada rekomendasi oli mesin, hanya ada gandar dan transmisi
                rek = product[0]['name'] rescue product['name'] rescue 'NULL2'
                alt = product[1]['name'] rescue 'NULL2'
                str = "#{eq['manufacturer']}\t#{eq['display_name_short']}\t#{eq['yearfrom']}\t#{eq['yearto']}\t#{rek}\t#{alt}\n"
                print str
                fr.write str
            end
            break if no_more
        end
    end
end