const lines = require('fs').readFileSync('/dev/stdin', 'utf8').split('\n');
const a = parseInt(lines[0]);
const b = parseInt(lines[1]);
console.log(a + b);