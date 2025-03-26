// config.js

const host = window.location.hostname;
let API_BASE_URL = "";

if (host.includes("fe8c:5c2d")) {
  // For Node 1
  API_BASE_URL = "http://[2605:fd00:4:1001:f816:3eff:fe8c:5c2d]:8000";
} else if (host.includes("fecc:9717")) {
  // For Node 2
  API_BASE_URL = "http://[2605:fd00:4:1001:f816:3eff:fecc:9717]:8000";
} else if (host.includes("fe3e:c88d")) {
  // For Node 3
  API_BASE_URL = "http://[2605:fd00:4:1001:f816:3eff:fe3e:c88d]:8000";
} else if (host.includes("fe30:2aee")) {
  // For Node 5
  API_BASE_URL = "http://[2605:fd00:4:1001:f816:3eff:fe30:2aee]:8000";
} else if (host.includes("fe2b:1955")){
  //For Node 6
  API_BASE_URL = "http://[2605:fd00:4:1001:f816:3eff:fe2b:1955]:8000";
} else if (host.includes("fe1d:66cc")){
  //For Node 12
  API_BASE_URL = "http://[2605:fd00:4:1001:f816:3eff:fe1d:66cc]:8000";
}
else {
  // Fallback – adjust as needed
  API_BASE_URL = "http://localhost:8000";
}

export { API_BASE_URL };
