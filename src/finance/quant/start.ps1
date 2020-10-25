$work=(get-item $PSScriptRoot)
Write-output "Mounting dir $work"
docker run -d -it --rm -p 8888:8888 -p 4040:4040  --env JUPYTER_ENABLE_LAB=true --name portfolio -v ${work}:/home/jovyan/work portfolio
