# Setup MiniMax MCP for Cursor

$env:Path = "C:\Users\SEMEN\.local\bin;$env:Path"

$cursorGlobalStorage = "$env:APPDATA\Cursor\User\globalStorage"

if (-not (Test-Path $cursorGlobalStorage)) {
    New-Item -ItemType Directory -Path $cursorGlobalStorage -Force | Out-Null
}

$mcpConfigPath = "$cursorGlobalStorage\mcp.json"

$config = @{
    mcpServers = @{
        minimax = @{
            command = "uvx"
            args = @("minimax-mcp")
            env = @{
                MINIMAX_API_KEY = "YOUR_API_KEY_HERE"
            }
        }
    }
}

$config | ConvertTo-Json -Depth 10 | Set-Content $mcpConfigPath -Encoding UTF8

Write-Host "Configuration saved to: $mcpConfigPath"
Write-Host ""
Write-Host "IMPORTANT: Replace YOUR_API_KEY_HERE with your actual MiniMax API key"
Write-Host "Get your API key at: https://platform.minimax.io/"
Write-Host ""
Write-Host "Next steps:"
Write-Host "1. Open the file and replace YOUR_API_KEY_HERE"
Write-Host "2. Restart Cursor completely"
Write-Host "3. Check MCP connection in Cursor Settings"

