// Native fetch is available in Node 18+
// remove import

const BASE_URL = 'https://cdb6-2401-4900-463d-983e-2872-81a9-e20e-f0bb.ngrok-free.app';

async function testEndpoint(name, path) {
    console.log(`Testing ${name} (${path})...`);
    try {
        const response = await fetch(`${BASE_URL}${path}`, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                'ngrok-skip-browser-warning': 'true'
            }
        });

        console.log(`Status: ${response.status}`);
        const text = await response.text();
        console.log(`Response: ${text.substring(0, 500)}...`);
    } catch (error) {
        console.error(`Error testing ${name}:`, error.message);
    }
    console.log('---');
}

async function run() {
    await testEndpoint('Summarize', '/summarize?topic=computer%20science%20101');
    await testEndpoint('Research', '/research?topic=computer%20science%20101');
}

run();
