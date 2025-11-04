<?php
date_default_timezone_set('UTC');

$u = $_POST['username'] ?? '';
$p = $_POST['password'] ?? '';
$source_ip = $_SERVER['REMOTE_ADDR'] ?? 'unknown';

$ok = ($u === 'admin' && $p === 'password'); // demo-only

$eventType = $ok ? 'login_success' : 'login_failed';
$message = $ok ? 'User logged in.' : 'Invalid credentials.';

# --- write to app log file ---
$logDir = __DIR__ . '/logs';
if (!is_dir($logDir)) { mkdir($logDir, 0777, true); }
$logFile = $logDir . '/app_events.log';

$line = json_encode([
  'ts' => date('c'),
  'source_ip' => $source_ip,
  'username' => $u,
  'event_type' => $eventType,
  'message' => $message
]) . PHP_EOL;

file_put_contents($logFile, $line, FILE_APPEND);

# --- insert into DB (best-effort) ---
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

} catch (Throwable $e) {
  $err = json_encode(['ts'=>date('c'),'level'=>'error','db_error'=>$e->getMessage()]) . PHP_EOL;
  file_put_contents($logFile, $err, FILE_APPEND);
}

# --- user feedback ---
if ($ok) {
  echo "<h2>Login successful</h2><p>Welcome, " . htmlspecialchars($u) . ".</p><p><a href='/'>Back</a></p>";
} else {
  echo "<h2>Login failed</h2><p>Try again.</p><p><a href='/'>Back</a></p>";
}