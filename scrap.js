const https = require( 'https' );
const util = require('util')
const fs = require('fs')

const hostname = 'www.bel1m0b1lgue.c0.1d';
const path = '/api/cardata'
const cacheDir = 'cacheScrap/'
const cookie = 'lastLocaleName=id; persist%3Aroot={"evaluation":"\"N4IgpgbghgNgIlALlEAuUAHGSxpCAGhAFsoBrXVfI4gewBMwY9CQBPMKAJxaMS4CWxXiBi0AxkgG0AdiOICYnAOaVq4UopHiBiNiIBGtWmTTAAvkRlRia1hgAWsu0UfOATCP5QZAZwW+vtJyVKwCfhhg4ojBACpskXgASgCisQCCAJIAMpkAcgDKAAopAMKxmQDyefaC0OJsRbQwAg3p4uJgGIho-ACuYJYg4b6R0cFN4T3oQwCOfbSIYJXdwb5mQ6QUKzGy66gA2iDpMABmUAAESbS2tKzpvoiyFwCy3DFyROl99AKsAEJgGSIJT6Ij-IQ+ZBcFDgl4AdVYpQcYC4YJAyMgXGaYB6RGRaN8Sh4RAQYAA7sZWAgBA4kL4+tT6X1PiA4AAxAoAaWpDFUrHZqJhggFAiQAtoXHoEqerIA4mAmOiABLhO5EZXNRiszUyeiwkDKvrEWwkw1sFn6v5ETIyU7hXTWkCZBkAL0ZRAAUlBlH1uKxPYqMKwuZl0qxsjYjFxlA4HRGfPQrrQIKiI2AAB59dZEN5cCBi1hvXyoqRFqBZnMgN6u-VF1GdRi+AC0gJkrqL+UyRd0DIMAl8cdYeQHvh8rEqMHo-lo-aUE8izCIRTAfVUi1YTS4vnEKM32NlrCSQKgfRgeJA1xgMF8ybYnVYBVIXAvBTHMmUAE1ZMpH30DNwHogAUfTumQTqxEgBqxEIkqsLEtBsIsBoAKpwBcsRJChpRcgUrAAGrNGQvjkj6QIEc0EDqiA8JnuEv4ALo0OQYCCkgfRcGA9A7GsaBHAhSHIKwup1qSUC0syf5gU6Ly9v+A5DkxJAMEwPF7HxSkcNwal+BpfCCMQOn7AcSneH4ARBLIRl6SQigqMsqzqYcSliJIuwyNZhwgP8sBOj5eosr+XpQEYjDIAYYCmLmXHjkQBRgM+PhBcBHEhVAbAGt+ygZWQ7woEpOgxGAvieSZRAGDCMi7qVSlEosNVEEoUD0AUtAcZ0JWObpzlECW+atGA8SRA1IAYNiyicYEaAAIxEPqyBFHUUANKUexAtMAAMc0CMouiwKtJosq0UiyKtfjrWgW0kMVJYfqiKF9AI0qhEQTiplwkzAiIvyPD4nRvBgGD0RsrjYEs8XLQ4BTIIg2ZoOcN5gEQA7ZLQzXA+go1g5QCMlsxFDw7AePKYwzCoLjSMgPwQiE4j+k+P4o7BLTxPiJxOClNw2ScM9FNEOIsj2lwxCc1w3PNSzlN9Bg81gKL4v0KU2ZPKaCBCeTROU01LVtVwHWS71qIFp0Q045r-OOsVBsgPMixm3TogSCdIQU0MJZKNEXEFGI0zqALdoCMLztFGRasoJjIxjO5n3TBYRAcTAIcwsQ+xxyARgmBsQwDi8DCwCs5EzPzXM85kz3qBVf0OEkUDkjV5hAA\"","_persist":"\"N4IgbgpgTgzglgewHYgFwFoCMAaEUIAWAngCZQCGALhCWpVAK4S4wA2ClA8gA6WJIw0AbQC6uAEYUkAYwIAlcgHcefZINSiAvkA\""}; utm_params=%7B%22utm_source%22%3A%22direct%22%7D; uDashIn=%7B%7D; uDashOut=%7B%7D; __exponea_etc__=2505875d-22fb-40a6-b48e-ebe752c4aa00; __exponea_time2__=2.310105323791504; __storejs__=%22__storejs__%22'
const userAgent = 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:77.0) Gecko/20100101 Firefox/77.0'

const merks = ["Alfa Romeo",
"Aston Martin",
"Audi",
"Bentley",
"Bimantara",
"BMW",
"Chery",
"Chevrolet",
"Chrysler",
"Daewoo",
"Daihatsu",
"Datsun",
"DFSK",
"Dodge",
"Ferrari",
"Fiat",
"Ford",
"Foton",
"Geely",
"Hino",
"Holden",
"Honda",
"Hummer",
"Hyundai",
"Infiniti",
"Isuzu",
"Jaguar",
"Jeep",
"KIA",
"Lamborghini",
"Land Rover",
"Lexus",
"Marvia",
"Maserati",
"Maxus",
"Mazda",
"Mercedes-Benz",
"MINI",
"Mitsubishi",
"Nissan",
"Oldsmobile",
"Opel",
"Peugeot",
"Porsche",
"Proton",
"Renault",
"Rolls Royce",
"Smart",
"SsangYong",
"Subaru",
"Suzuki",
"Tata",
"Timor",
"Toyota",
"UD TRUCKS",
"Volkswagen",
"Volvo",
"Wuling"]

const merk2model = (merk) => '{model(country:"ID",make:"'+merk+'"){list}}';
const model2year = (merk,model) => '{year(country:"ID",make:"'+merk+'",model:"'+model+'"){list}}';
const year2tipe = (merk,model,year) => '{trim(country:"ID",make:"'+merk+'",model:"'+model+'",year:'+year+'){list}}';
const tipe2trans = (merk,model,year,tipe) => '{transmission(country:"ID",make:"'+merk+'",model:"'+model+'",year:'+year+',trim:"'+tipe+'"){list}}'

function get( keys, callback ) {
    const fname = cacheDir + keys.join('__').split('/').join('_') + '.json';
    if(fs.existsSync(fname)) {
        fs.readFile(fname, 'utf8', function(err, data) {
            if (err) console.log(data);
            callback(JSON.parse(data));
        })
        return;
    }
    let postData = (
        keys.length == 1? merk2model(keys[0]) :
        keys.length == 2? model2year(keys[0],keys[1]) :
        keys.length == 3? year2tipe(keys[0],keys[1],keys[2]) :
        tipe2trans(keys[0],keys[1],keys[2],keys[3])
    );
    const options = {
        hostname: hostname,
        port: 443,
        path: path,
        method: 'POST',
        headers: {
            'Content-Type':'application/graphql',
            'Cookie':cookie,
            'User-Agent': userAgent,
            'Content-Length': postData.length
        }
    }
	let req = https.request(options, ( res ) => {
		let error;
		if( res.statusCode!==200 ) {
			error = new Error( 'Request Failed.\n' +
				`Status Code: ${res.statusCode}` );
		}
		if( error ) {
			console.error( error.message );
			// Consume response data to free up memory
			res.resume();
			return;
		}
		res.setEncoding( 'utf8' );
		let json = '';
		res.on( 'data', ( chunk ) => {
			json += chunk;
		} );
		res.on( 'end', () => {
            console.log( json );
            fs.writeFileSync(fname,json);
            callback( JSON.parse( json ) );
		} );
	} ).on( 'error', ( e ) => {
		console.error( `Got error: ${e.message}` );
    } );
    req.write(postData);
    req.end();
}

let matrix = '';
let total = merks.length;
let done = 0;
for(var z in merks) {
    const merk = merks[z];
    get([merk],function(res){
        let models = res.data.model.list;
        total += models.length;
        done += 1;
        for(var y in models) {
            const model = models[y];
            get([merk,model],function(res){
                let years = res.data.year.list;
                total += years.length;
                done += 1;
                for(var x in years) {
                    const year = years[x];
                    get([merk,model,year],function(res){
                        let trims = res.data.trim.list;
                        total += trims.length;
                        done += 1;
                        for(var v in trims) {
                            const trim = trims[v];
                            get([merk,model,year,trim],function(res){
                                matrix += merk + "\t" + model + "\t" + year + "\t" + trim + "\t" + res.data.transmission.list.join(',') + "\n";
                                done += 1;
                                console.log(done+'/'+total)
                                if(done == total) {
                                    fs.writeFileSync('matrix.tsv',matrix);
                                }
                            })
                        }
                    })
                }
            })
        }
    })
}