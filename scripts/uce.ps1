$RESYST = "..\main.py"
$TRG_RESULTS = "D:\src\resyst\ReSyst\data\results\uce_trg_results.json"
$TRG_RATIO = 0.9

Clear-Host

if ([System.IO.File]::Exists($TRG_RESULTS)) {
	c:\python34\python.exe $RESYST -a test --training-file $TRG_RESULTS --testing-ratio $TRG_RATIO
} else {
	Write-Host "[-] Could not find training file '$TRG_RESULTS'."
}


