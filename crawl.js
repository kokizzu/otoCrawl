const https = require( 'https' );
const util = require('util')

const hostname = 'https://0t0m4ll.id';

const makes = '/catalog/cars/makes';

function modelname( maker ) {
	return '/catalog/cars/modelnames?make=' + maker;
}

function generations( maker, model ) {
	return '/catalog/cars/generations?make=' + maker + '&modelName=' + model;
}

function get( path, callback ) {
	https.get( hostname + path, ( res ) => {
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
			callback( JSON.parse( json ) );
		} );
	} ).on( 'error', ( e ) => {
		console.error( `Got error: ${e.message}` );
	} )
}

var result = {};
var total = 0;
get( makes, function( makers ) {
	for( var z in makers ) {
		const maker = makers[ z ];
		result[ maker ] = {};
		get( modelname( maker ), function( models ) {
			total += models.length;
			for( var y in models ) {
				const model = models[ y ];
				get( generations( maker, model ), function( gens ) {
					result[ maker ][ model ] = gens;
					if( --total == 0 ) {
						console.log(util.inspect(result, {showHidden: false, depth: null}))
					}
				} )
			}
		} )
	}
} );
