/**
 * Created by danielbachar on 15/03/2019.
 */

const loadtest = require('loadtest');

const options = {
	url: 'http://35.239.69.254:31001/service',
	maxRequests: 100,
    maxSeconds:200,
    concurrency:1,
    requestsPerSecond:1 ,

};


function startYoYoAttack(options) {
	loadtest.loadTest(options, function(error, result) {
	if (error)
	{
		return console.error('Got an error: %s', error);
	}
	console.log('Tests run successfully');
	console.log(result);
});
}


function start() {
	//TODO
	/*
		1) Start steady requests of 10 rps
	 */
}
// loadtest -c 2 --rps 4 http://35.239.69.254:31001/service