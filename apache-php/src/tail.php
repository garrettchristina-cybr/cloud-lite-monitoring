<?php
header('Content-Type: text/plain');
$path = __DIR__ . '/logs/app_events.log';
if (!file_exists($path)) { echo "No log"; exit; }
echo `tail -n 200 $path`;