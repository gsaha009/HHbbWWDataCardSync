import os
import argparse
import json
import copy
import ROOT

class SyncResults:
    def __init__(self, inJSON, bambooOutDir, talinnDir, uclDir, hist1Name, hist2Name, talinnfname, var, era, createPreSyncFiles, compareHists):
        
        self.inJSON        = inJSON
        self.bambooOutDir  = bambooOutDir
        self.talinnDir     = talinnDir
        self.uclDir        = uclDir
        self.hist1Name     = hist1Name
        self.hist2Name     = hist2Name
        self.talinnfname   = talinnfname
        self.var           = var 
        self.era           = era
        
        self.dictJson = self.loadJSON (self.inJSON)
        if createPreSyncFiles: 
            if not self.createFile (self.dictJson, 
                                    self.bambooOutDir, 
                                    self.talinnDir, self.uclDir, 
                                    self.hist1Name, self.hist2Name, 
                                    self.talinnfname, self.era):
                raise RuntimeError("Dhyat! Bhule bhora Bosundhora :: Age file bana")
            else:
                print("UCL preSync files created!!")

        if compareHists:        
            if not self.makeComparison (self.dictJson, 
                                        self.talinnDir, self.uclDir,
                                        self.talinnfname, 
                                        self.var, self.era):
                raise RuntimeError("Dhyat! Bhule bhora Bosundhora :: Check kor")
            else:
                print("Sync histograms created!")
        
        else:
            print('No preSync files created or compared!')
            

    def loadJSON (self, inJSON):
        with open(inJSON) as file:
            cfgDict = json.load(file)
        pwd=os.getcwd()
        #print 'Working Directory: %s'%(pwd)
        return cfgDict


    def createFile (self, dictJson, bambooOutDir, talinnDir, uclDir, hist1Name, hist2Name, talinnfname, era):
        if not os.path.exists(uclDir):
            os.mkdir(uclDir)
        # Create an output file
        outf = ROOT.TFile.Open (uclDir+'/'+talinnfname+'_UCL.root', 'RECREATE')
        outf.mkdir('HH_1l_0tau')
        lumi = 0.0
        if era=='2016':
            lumi = 35922.0
        if era=='2017':
            lumi = 40000.0
        if era=='2018':
            lumi = 80000.0
        for key, value in dictJson.items():
            print 'Group: %s'%(key)
            outhist = None
            for v in value:
                sameHist = True if hist1Name==hist2Name else False
                if v.startswith('#') or v.startswith('//'):
                    continue
                subval = v.split(":")
                head = subval[0]
                if era in head:
                    #print (head)
                    lumi = 1.0
                #lumi = float(subval[1])
                xsec = float(subval[1])
                wtsum = float(subval[2])
                br = float(subval[3])
                lumifac = (lumi*xsec*br)/wtsum
                file = os.path.join(os.path.join(os.getcwd(),bambooOutDir),head+'.root')
                if not os.path.isfile(file):
                    raise RuntimeError("%s doesn't exist in %s"%(file,os.getcwd()))
                histFile = ROOT.TFile.Open(file ,"READ")
                h1Dist   = histFile.Get(hist1Name)
                #print(type(h1Dist))
                if not sameHist:
                    h2Dist   = histFile.Get(hist2Name)
                    h2Dist.Scale(lumifac)
                h1Dist.Scale(lumifac)
                if outhist is None:
                    outhist  = h1Dist.Clone()
                    if not sameHist:
                        outhist.Add(h2Dist)
                else:
                    outhist.Add(h1Dist)
                    if not sameHist:
                        outhist.Add(h2Dist)
                outhist.SetDirectory(0)
            # Write the cumulative histo 
            outhist.SetName(key)
            outf.cd('HH_1l_0tau')
            outhist.Write()

        outf.Close()
        return True

    def makeComparison (self, dictJson, talinnDir, uclDir, talinnfname, var, era):
        file1 = ROOT.TFile.Open(os.path.join(uclDir,talinnfname+'_UCL.root'), "READ")
        file2 = ROOT.TFile.Open(os.path.join(talinnDir,talinnfname+'.root'), "READ")

        index = 0
        if not os.path.exists('SyncOut'):
            os.mkdir('SyncOut')
        root_file = ROOT.TFile('SyncOut/'+talinnfname+'_UCL_Ratio_'+era+'.root',"recreate")
        for key_ in dictJson.keys():
            key = str(key_)
            findname = os.path.join('HH_1l_0tau',key)
            #print (findname)
            file1.cd()
            histN = file1.Get(findname)
            #print type(histN)
            histN.SetDirectory(0)

            file2.cd()
            histD = file2.Get(findname)
            #print type(histD)
            histD.SetDirectory(0)

            #print type(hist1), type(hist2)
            histR = self.createRatio(histN, histD)
            self.saveToRoot (histD, histN, histR, root_file, key)
            canvas = 'c_'+str(key_)
            canvas, legend = self.ratioplot(histN, histD, histR, var, key)
            #canvas.SaveAs('Output/'+key+'_'+talinnfname+'_UCL.pdf')
            if index == 0:
                canvas.Print('SyncOut/'+talinnfname+'_UCL_Ratio_'+era+'.pdf[')
            canvas.Print('SyncOut/'+talinnfname+'_UCL_Ratio_'+era+'.pdf')
            index = index + 1

        canvas.Print('SyncOut/'+talinnfname+'_UCL_Ratio_'+era+'.pdf]')
        return True
    
    @staticmethod
    def createRatio(h1, h2):
        h3 = h1.Clone("h3")
        #h3.Sumw2()
        #h3.SetStats(0)
        h3.Divide(h2)
        return h3
        
    @staticmethod
    def ratioplot(h1,h2,h3,label,title):
        C = ROOT.TCanvas("c1", "c1", 600, 600)
        C.Divide(1,2)
        colors = [418,602]
        #leg = ROOT.TLegend(0.65,0.60,0.90,0.80)
        leg = ROOT.TLegend(0.7826962,0.7050093,0.9979879,0.8961039)
        leg.SetBorderSize(0)
        leg.SetTextSize(0.05)

        C.cd(1)
        ROOT.gPad.SetRightMargin(0.05)
        ROOT.gPad.SetLeftMargin(0.15)
        ROOT.gPad.SetTopMargin(0.15)
        ROOT.gPad.SetBottomMargin(0.01)
        ROOT.gPad.SetLogy()
        ROOT.gPad.SetGrid(1)

        ROOT.gStyle.SetTitleFontSize(0.1)
        ROOT.gStyle.SetOptStat(0)

        h1.SetTitle(title)
        h1.GetYaxis().SetTitle("")
        h1.GetYaxis().SetTitleOffset(1.)
        h1.GetYaxis().SetLabelSize(0.05)
        h1.GetYaxis().SetTitleSize(0.06)
        h1.GetXaxis().SetTitle("")
        h1.GetXaxis().SetLabelSize(0.)

        h1.SetLineWidth(2)
        h1.SetLineColor(1)
        h2.SetLineWidth(2)
        h2.SetLineColor(2)

        hmax = max([h1.GetMaximum(),h2.GetMaximum()])
        h1.SetMaximum(hmax*1.5)

        leg.AddEntry(h1,'UCL')
        leg.AddEntry(h2,'Talinn')

        h1.Draw("H")
        h2.Draw("H same")
    
        leg.Draw()
    
        C.cd(2)
        ROOT.gPad.SetRightMargin(0.05)
        ROOT.gPad.SetLeftMargin(0.15)
        ROOT.gPad.SetTopMargin(0.01)
        ROOT.gPad.SetBottomMargin(0.15)
        ROOT.gPad.SetGridy()

        h3.SetTitle("")
        h3.SetLineWidth(2)
        h3.SetLineColor(1)

        h3.SetMaximum(h3.GetMaximum()*1.1)
        h3.SetMinimum(h3.GetMinimum()*0.9)

        h3.GetYaxis().SetRangeUser(0.0,1.5)

        h3.GetYaxis().SetTitle("#frac{UCL}{Talinn}")
        h3.GetYaxis().SetLabelSize(0.05)
        h3.GetYaxis().SetTitleSize(0.06)
        h3.GetYaxis().SetTitleOffset(1.)

        h3.GetXaxis().SetTitle(label)
        h3.GetXaxis().SetLabelSize(0.05)
        h3.GetXaxis().SetTitleSize(0.06)

        h3.Draw("PE")

        #C.Print(self.outputname+'_%s_%s.pdf'%(sample,self.era))
        return C,leg

    @staticmethod     
    def saveToRoot(den,num,ratio,rootFile,dirc):
        rootFile.cd()
        rootFile.mkdir(dirc)
        rootFile.cd(dirc)
        #root_file = ROOT.TFile('Output/'+fname+'_UCL_Ratio.root',"recreate")
        den.Write("Talinn")
        num.Write("UCL")
        ratio.Write("ratio")
        rootFile.Write()
        #rootFile.Close()
       
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Sync between Talinn & UCL :: args: 1. --exeJson=VarHistFiles.json, 2. --makePreSyncFiles or if its done, then --syncHistograms')
    parser.add_argument('--exeJson', action='store', required=True, type=str, default='',
                        help='This JSON contains all the histogram names, variable names, talinn file names. It is damn important..! Must Must Must provide it [e.g. VarHistFile.json]')
    parser.add_argument('--category', action='store', required=False, type=str, default='All',
                        help='Want to see the synced plots for 1b or/and 2b or/and Sb || All ?')
    parser.add_argument('--era', action='store', required=False, type=str, default='2016',
                        help='mention era [important to get the luminosity]')
    parser.add_argument('--inFile', action='store', required=False, type=str, default='syncthemall.json',
                        help='JSON file with all the input files, their xsec, evWtSum, BR and target lumi')
    parser.add_argument('--bambooOut', action='store', required=False, type=str, default='SL_BDT/results',
                        help='Bamboo output directory with root files [e.g. SL_test/results]')
    parser.add_argument('--talinnDir', action='store', required=False, type=str, default='TalinnRootFiles',
                        help='dir with UCL files with same structure as Talinn')
    parser.add_argument('--uclDir', action='store', required=False, type=str, default='UclRootFiles',
                        help='dir with UCL files with same structure as Talinn')
    parser.add_argument('--makePreSyncFiles', action='store_true', default=False,
                        help='Create the files with same structure as talinn')
    parser.add_argument('--syncHistograms', action='store_true', default=False,
                        help='Comparing the histograms [Warning! Create preSyncedFiles and then make it run]')
    
    args = parser.parse_args()
    
    varHistDict = None
    with open(args.exeJson) as hfile:
        varHistDict = json.load(hfile)
    
    for catkey, infoDictList in varHistDict.items():
        print 'Category: %s'%(catkey)
        for infoDict in infoDictList:
            valList = [str(val) for val in infoDict.values()]
            print 'channel:  %s'%('El' if '_e_' in valList[2] else 'Mu'),'\t', 'var:  %s'%(valList[0])
            SyncResults(inJSON             = args.inFile,
                        bambooOutDir       = args.bambooOut,
                        talinnDir          = args.talinnDir,
                        uclDir             = args.uclDir,
                        hist1Name          = valList[1],
                        hist2Name          = valList[3],
                        talinnfname        = valList[2],
                        var                = valList[0],
                        era                = args.era,
                        createPreSyncFiles = args.makePreSyncFiles,
                        compareHists       = args.syncHistograms)
            
