# deploy.ps1

# Read secrets from secrets.env
$envFile = "d:\github\user1\Todo-Full-stack\secrets.env"
if (-not (Test-Path $envFile)) {
    Write-Error "secrets.env not found in parent directory!"
    exit 1
}

# Function to encode base64
function ConvertTo-Base64($string) {
    if ([string]::IsNullOrEmpty($string)) { return "" }
    $bytes = [System.Text.Encoding]::UTF8.GetBytes($string)
    $encoded = [System.Convert]::ToBase64String($bytes)
    return $encoded
}

# Read variables from .env file
$envContent = Get-Content $envFile
$secrets = @{}

foreach ($line in $envContent) {
    if ($line -match "^\s*#") { continue } # Skip comments
    if ($line -match "^\s*$") { continue } # Skip empty lines
    
    $parts = $line -split "=", 2
    if ($parts.Count -eq 2) {
        $key = $parts[0].Trim()
        $value = $parts[1].Trim()
        $secrets[$key] = $value
        Write-Host "Found key: '$key'"
    }
}

# Verify DATABASE_URL
if (-not $secrets.ContainsKey("DATABASE_URL")) {
    Write-Error "DATABASE_URL not found in secrets.env (check for BOM or encoding issues)"
    # Clean keys if needed
    foreach ($k in $secrets.Keys) {
        if ($k -match "DATABASE_URL") {
            Write-Host "Found similar key: '$k' - Ascii: $([int[]][char[]]$k -join ',')"
        }
    }
}

# Encode secrets
$databaseUrl = ConvertTo-Base64 $secrets["DATABASE_URL"]
$geminiApiKey = ConvertTo-Base64 $secrets["GEMINI_API_KEY"]
$jwtSecret = ConvertTo-Base64 $secrets["JWT_SECRET"]
$betterAuthSecret = ConvertTo-Base64 $secrets["BETTER_AUTH_SECRET"]
$googleClientId = ConvertTo-Base64 $secrets["GOOGLE_CLIENT_ID"]
$googleClientSecret = ConvertTo-Base64 $secrets["GOOGLE_CLIENT_SECRET"]
$accessTokenExpireMinutes = ConvertTo-Base64 $secrets["ACCESS_TOKEN_EXPIRE_MINUTES"]
$refreshTokenExpireDays = ConvertTo-Base64 $secrets["REFRESH_TOKEN_EXPIRE_DAYS"]
$googleRedirectUri = ConvertTo-Base64 $secrets["GOOGLE_REDIRECT_URI"]

# Run Helm Install
helm upgrade --install focusflow-release . `
  --namespace todo-ns `
  --set secrets.databaseUrl=$databaseUrl `
  --set secrets.geminiApiKey=$geminiApiKey `
  --set secrets.jwtSecret=$jwtSecret `
  --set secrets.betterAuthSecret=$betterAuthSecret `
  --set secrets.googleClientId=$googleClientId `
  --set secrets.googleClientSecret=$googleClientSecret `
  --set secrets.accessTokenExpireMinutes=$accessTokenExpireMinutes `
  --set secrets.refreshTokenExpireDays=$refreshTokenExpireDays `
  --set secrets.googleRedirectUri=$googleRedirectUri `
  --set frontend.image.tag=latest `
  --set backend.image.tag=latest

Write-Host "Deployment initiated successfully!"
