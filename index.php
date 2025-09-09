<?php
// PHP bridge for Divine Tribe Marketing Hub
// This executes the Python Flask app and serves it through PHP

// Set proper headers
header('Content-Type: text/html; charset=UTF-8');

// Change to the tools directory
chdir(__DIR__);

// Execute Python Flask app and capture output
$command = 'python3 -c "
import sys
sys.path.insert(0, \".\")
from flask_wrapper import app
with app.test_client() as client:
    response = client.get(\"/\")
    print(response.get_data(as_text=True))
"';

$output = shell_exec($command . ' 2>&1');

if ($output) {
    echo $output;
} else {
    echo '<html><body><h1>Error</h1><p>Could not load Python application</p></body></html>';
}
?>

