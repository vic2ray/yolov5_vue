let CONFIG = {};
const protocol = window.location.protocol; 
const hostname = window.location.hostname; 
// CONFIG.flaskUrl = protocol + "//" + hostname + ":5000"
// CONFIG.tensorboardUrl = protocol + "//" + hostname + ":6006"
CONFIG.flaskUrl = protocol + "//" + hostname + "/flask"
CONFIG.tensorboardUrl = protocol + "//" + hostname + "/tensorboard"