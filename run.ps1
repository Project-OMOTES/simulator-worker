# load environment variables
get-content .env | foreach {
    if ($_.length -gt 1) {
        $name, $value = $_.split('=')
        Write-Host "Environment var: $name = $value"
        set-content env:\$name $value    
    }
}

# simulator_worker