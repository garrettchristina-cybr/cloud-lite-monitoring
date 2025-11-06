<?php
// SPDX-License-Identifier: MIT
date_default_timezone_set('UTC');

/* Only accept POSTs */
if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
  http_response_code(405);
  echo "<h2>Method Not Allowed</h2><p>Submit the form.</p><p><a href='/'>Back</a></p>";
  exit;
}

/* Read fields */
$u = $_POST['username'] ?? '';
$p = $_POST['password'] ?? '';

/* Source IP (prefer X-Forwarded-For) */
$source_ip = $_SERVER['REMOTE_ADDR'] ?? 'unknown';
if (!empty($_SERVER['HTTP_X_FORWARDED_FOR'])) {
  $xff_first = trim(explode(',', $_SERVER['HTTP_X_FORWARDED_FOR'])[0]);
  if (filter_var($xff_first, FILTER_VALIDATE_IP)) $source_ip = $xff_first;
}

/* Demo auth */
$ok = ($u === 'admin' && $p === 'password');
$eventType = $ok ? 'login_success' : 'login_failed';
$message   = $ok ? 'User logged in.' : 'Invalid credentials.';

/* Ensure logs dir exists */
$logDir = __DIR__ . '/logs';
if (!is_dir($logDir)) { @mkdir($logDir, 0777, true); }

/* Geo lookup with simple cache (ipapi.co) */
$geo = ['geo_country'=>null,'geo_city'=>null,'geo_lat'=>null,'geo_lon'=>null];
try {
  $cacheFile = __DIR__ . '/geo_cache.json';
  $cache = file_exists($cacheFile) ? json_decode(file_get_contents($cacheFile), true) : [];
  if (!is_array($cache)) $cache = [];
  if (isset($cache[$source_ip])) {
    $geo = $cache[$source_ip];
  } else {
    $resp = @file_get_contents("https://ipapi.co/{$source_ip}/json/");
    if ($resp) {
      $j = json_decode($resp, true);
      if (is_array($j)) {
        $geo = [
          'geo_country' => $j['country_name'] ?? null,
          'geo_city'    => $j['city'] ?? null,
          'geo_lat'     => isset($j['latitude'])  ? (float)$j['latitude']  : null,
          'geo_lon'     => isset($j['longitude']) ? (float)$j['longitude'] : null
        ];
        $cache[$source_ip] = $geo;
        @file_put_contents($cacheFile, json_encode($cache));
      }
    }
  }
} catch (Throwable $e) { /* ignore geo errors for demo */ }

/* Build JSON line */
$line = json_encode([
  'ts'         => date('c'),
  'source_ip'  => $source_ip,
  'username'   => $u,
  'event_type' => $eventType,
  'message'    => $message,
  'geo_country'=> $geo['geo_country'],
  'geo_city'   => $geo['geo_city'],
  'geo_lat'    => $geo['geo_lat'],
  'geo_lon'    => $geo['geo_lon'],
  'user_agent' => $_SERVER['HTTP_USER_AGENT'] ?? 'unknown'
], JSON_UNESCAPED_SLASHES) . PHP_EOL;

/* Write to app log */
$logFile = $logDir . '/app_events.log';
@file_put_contents($logFile, $line, FILE_APPEND);

/* Best-effort DB insert (optional; safe to skip on error) */
try {
  $dsn = sprintf('mysql:host=%s;dbname=%s;charset=utf8mb4', getenv('DB_HOST'), getenv('DB_NAME'));
  $dbh = new PDO($dsn, getenv('DB_USER'), getenv('DB_PASS'), [PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION]);
  $dbh->exec("CREATE TABLE IF NOT EXISTS events (
    id INT AUTO_INCREMENT PRIMARY KEY,
    ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    source_ip VARCHAR(64),
    username VARCHAR(128),
    event_type VARCHAR(64),
    message TEXT
  )");
  $stmt = $dbh->prepare("INSERT INTO events (source_ip, username, event_type, message) VALUES (?, ?, ?, ?)");
  $stmt->execute([$source_ip, $u, $eventType, $message]);
} catch (Throwable $e) { /* ignore DB errors for demo */ }

/* User feedback + proper status */
http_response_code($ok ? 200 : 401);
echo $ok
  ? "<h2>Login successful</h2><p>Welcome, " . htmlspecialchars($u) . ".</p><p><a href='/'>Back</a></p>"
  : "<h2>Login failed</h2><p>Try again.</p><p><a href='/'>Back</a></p>";