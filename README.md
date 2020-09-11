*Synchronization*

First, locate the talinn root files and bambooOutDir/results 

```
python syncthemall.py <args>
```

*args:*

```
--exeJson VarHistFile.json
--category ::not important
--era 2016/2017/2018 [only one era per time]
--inFile syncthemall.json
--bambooOut SL_BDT/results :: Hardcoded
--talinnDir TalinnRootFiles ::Hardcoded
--uclDir UclRootFiles :: Hardcoded
--makePreSyncFiles :: To make root files as same structure as Talinn
--syncHistograms   :: make ratio plots for sync	
```
```
python syncthemall.py --exeJson VarHistFile.json --era 2016 --inFile syncthemall.json --makePreSyncFiles --syncHistograms
```