#!/usr/bin/env python
import sys
import re
import os
import argparse

helpText = "[leptons] = '2los', '3los'\n\
[region] = 'sr', 'sr_col', 'cr_dy', 'cr_tt', cr_vv', 'cr_ss', 'cr_wz', 'appl'\n\
[bin] = 'min', 'low', 'med', 'high'"
parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter,
                                 epilog=helpText)
parser.add_argument("outDir", help="Choose the output directory.\nOutput will be saved to 'outDir/year/conf'")
parser.add_argument("year", help="Choose the year: '2016', '2017' or '2018'")
parser.add_argument("conf", help="Specify the configuration to run in the format:\n[leptons]_[region]_[bin]")
parser.add_argument("--data", action="store_true", default=False, help="Include data")
parser.add_argument("--norm", action="store_true", default=False, help="Normalize signal to data")
parser.add_argument("--unc", action="store_true", default=False, help="Include uncertainties")
parser.add_argument("--sP", nargs='*', default=[], help="Include specific plots")
parser.add_argument("--xP", nargs='*', default=[], help="Exclude specific plots")
args = parser.parse_args()

ODIR=args.outDir
YEAR=args.year
lumis = {
'2016': '35.9', # '33.2' for low MET
'2017': '41.53', # '36.74' for low MET
'2018': '59.74',
}
if YEAR not in ("2016","2017","2018"): raise RuntimeError("Unknown year: Please choose '2016', '2017' or '2018'")
LUMI= " -l %s "%(lumis[YEAR])


submit = '{command}' 
dowhat = "plots" 
#dowhat = "dumps" 
#dowhat = "yields" 
#dowhat = "ntuple"

P0="/eos/cms/store/cmst3/group/tthlep/peruzzi/NanoTrees_SOS_230819_v5/"
nCores = 8
TREESALL = " --Fs {P}/recleaner -P "+P0+"%s "%(YEAR,)

def base(selection):
    CORE=TREESALL
    CORE+=" -f -j %d --split-factor=-1 --year %s --s2v -L susy-sos-v2-clean/functionsSOS.cc -L susy-sos-v2-clean/functionsSF.cc --tree NanoAOD --mcc susy-sos-v2-clean/mcc_sos.txt --mcc susy-sos-v2-clean/mcc_triggerdefs.txt "%(nCores,YEAR) # --neg"
    if YEAR == "2017": CORE += " --mcc susy-sos-v2-clean/mcc_METFixEE2017.txt "
    RATIO= " --maxRatioRange 0.0  1.99 --ratioYNDiv 505 "
    RATIO2=" --showRatio --attachRatioPanel --fixRatioRange "
    LEGEND=" --legendColumns 2 --legendWidth 0.25 "
    LEGEND2=" --legendFontSize 0.042 "
    SPAM=" --noCms --topSpamSize 1.1 --lspam '#scale[1.1]{#bf{CMS}} #scale[0.9]{#it{Preliminary}}' "
    if dowhat == "plots": CORE+=LUMI+RATIO+RATIO2+LEGEND+LEGEND2+SPAM+" --showMCError "


    wBG = " --alias wBG '1.0' "
    #wFS = " --alias wFS '1.0' "
    if selection=='2los':
         GO="%s susy-sos-v2-clean/mca/mca-2los-%s.txt susy-sos-v2-clean/2los_cuts.txt "%(CORE, YEAR)

         if YEAR == "2016":
             wBG = " --alias wBG 'puw_nInt_Moriond(nTrueInt)*getLepSF_16(LepGood1_pt, LepGood1_eta, LepGood1_pdgId)*getLepSF_16(LepGood2_pt, LepGood2_eta, LepGood2_pdgIdg)*triggerSFfullsim(LepGood1_pt, LepGood1_eta, LepGood2_pt, LepGood2_eta, met_pt, metmm_pt(LepGood1_pdgId, LepGood1_pt, LepGood1_phi, LepGood2_pdgId, LepGood2_pt,LepGood2_phi, met_pt, met_phi))' " #*bTagWeight
             #wFS = " --alias wFS 'getLepSFFS(LepGood1_pt, LepGood1_eta, LepGood1_pdgId)*getLepSFFS(LepGood2_pt, LepGood2_eta, LepGood2_pdgId)*ISREwkCor*bTagWeightFS*triggerEff(LepGood1_pt, LepGood1_eta, LepGood2_pt,LepGood2_eta, met_pt, metmm_pt(LepGood1_pdgId, LepGood1_pt, LepGood1_phi, LepGood2_pdgId, LepGood2_pt, LepGood2_phi, met_pt, met_phi))' "
         elif YEAR == "2017": 
             wBG = " --alias wBG 'vtxWeight2017*getLepSF_17(LepGood1_pt, LepGood1_eta, LepGood1_pdgId)*getLepSF_17(LepGood2_pt, LepGood2_eta, LepGood2_pdgId)' "
         elif YEAR == "2018":
             wBG = " --alias wBG '1.0' "
         GO="%s %s -W wBG"%(GO,wBG)

         if dowhat == "plots": GO=GO.replace(LEGEND, " --legendColumns 3 --legendWidth 0.52 ")
         if dowhat == "plots": GO=GO.replace(RATIO,  " --maxRatioRange 0.6  1.99 --ratioYNDiv 210 ")
         GO += " --binname 2los "
 
    elif selection=='3l':
        GO="%s susy-sos-v2-clean/mca-3l-%s.txt susy-sos-v2-clean/3l_cuts.txt "%(CORE,YEAR)
        
        if YEAR == "2016":
            wBG = " --alias wBG 'puw_nInt_Moriond(nTrueInt) *getLepSF_16(LepGood1_pt, LepGood1_eta, LepGood1_pdgId)*getLepSF_16(LepGood2_pt, LepGood2_eta, LepGood2_pdgId)*getLepSF_16(LepGood3_pt, LepGood3_eta, LepGood3_pdgId)*triggerSFfullsim3L(LepGood1_pt, LepGood1_eta, LepGood2_pt, LepGood2_eta, LepGood3_pt, LepGood3_eta, met_pt, metmmm_pt(LepGood1_pt, LepGood1_phi, LepGood2_pt, LepGood2_phi, LepGood3_pt, LepGood3_phi, met_pt, met_phi, lepton_Id_selection(LepGood1_pdgId, LepGood2_pdgId, LepGood3_pdgId)), lepton_permut(LepGood1_pdgId, LepGood2_pdgId, LepGood3_pdgId))' " #*bTagWeight
            #wFS = " --alias wFS 'getLepSFFS(LepGood1_pt, LepGood1_eta, LepGood1_pdgId) * getLepSFFS(LepGood2_pt, LepGood2_eta, LepGood2_pdgId) * getLepSFFS(LepGood3_pt, LepGood3_eta, LepGood3_pdgId)*ISREwkCor*bTagWeightFS * triggerEff3L(LepGood1_pt, LepGood1_eta, LepGood2_pt, LepGood2_eta, LepGood3_pt, LepGood3_eta, met_pt, metmmm_pt(LepGood1_pt, LepGood1_phi, LepGood2_pt, LepGood2_phi, LepGood3_pt, LepGood3_phi, met_pt, met_phi, lepton_Id_selection(LepGood1_pdgId, LepGood2_pdgId, LepGood3_pdgId)), lepton_permut(LepGood3_pdgId, LepGood3_pdgId, LepGood3_pdgId))' "
        elif YEAR == "2017":
            wBG = " --alias wBG 'vtxWeight2017*getLepSF_17(LepGood1_pt, LepGood1_eta, LepGood1_pdgId)*getLepSF_17(LepGood2_pt, LepGood2_eta, LepGood2_pdgId)*getLepSF_17(LepGood3_pt, LepGoog3_eta, LepGood3_pdgId)' "
            #wFS = " --alias wFS 1.0 "
        elif YEAR == "2018":
             wBG = " --alias wBG '1.0' "
        GO="%s %s -W wBG"%(GO,wBG)

        if dowhat == "plots": GO=GO.replace(LEGEND, " --legendColumns 3 --legendWidth 0.42 ")
        GO += " --binname 3l "

    else:
        raise RuntimeError('Unknown selection')

    if dowhat in ["plots","ntuple"]: GO+=" susy-sos-v2-clean/2los_3l_plots.txt "

    return GO

def promptsub(x):
    procs = [ '' ]
    if dowhat == "cards": procs += ['_FRe_norm_Up','_FRe_norm_Dn','_FRe_pt_Up','_FRe_pt_Dn','_FRe_be_Up','_FRe_be_Dn','_FRm_norm_Up','_FRm_norm_Dn','_FRm_pt_Up','_FRm_pt_Dn','_FRm_be_Up','_FRm_be_Dn']
    return x + ' '.join(["--plotgroup data_fakes%s+='.*_promptsub%s'"%(x,x) for x in procs])+" --neglist '.*_promptsub.*' "

def procs(GO,mylist):
    return GO+' '+" ".join([ '-p %s'%l for l in mylist ])

def sigprocs(GO,mylist):
    return procs(GO,mylist)+' --showIndivSigs --noStackSig'

def runIt(GO,name):
    if args.data: name=name+"_data"
    if args.norm: name=name+"_norm"
    if args.unc: name=name+"_unc"
    if dowhat == "plots":  print submit.format(command=' '.join(['python mcPlots.py',"--pdir %s/%s/%s"%(ODIR,YEAR,name),GO,' '.join(['--sP %s'%p for p in args.sP]),' '.join(['--xP %s'%p for p in args.xP])]))
    # What is supposed to be included in sys.argv[4] and after?
    #elif dowhat == "yields": print 'echo %s; python mcAnalysis.py'%name,GO,' '.join(sys.argv[4:])
    #elif dowhat == "dumps":  print 'echo %s; python mcDump.py'%name,GO,' '.join(sys.argv[4:])
    #elif dowhat == "ntuple": print 'echo %s; python mcNtuple.py'%name,GO,' '.join(sys.argv[4:])

def add(GO,opt):
    return '%s %s'%(GO,opt)

def setwide(x):
    x2 = add(x,'--wide')
    x2 = x2.replace('--legendWidth 0.35','--legendWidth 0.20')
    return x2

def binYearChoice(x,torun,YEAR):
    metBin = ''
    if '_min' in torun:
        metBin = 'met75'
    elif '_low' in torun:
        metBin = 'met125'
    elif '_med' in torun:
        metBin = 'met200'
    elif '_high' in torun:
        metBin = 'met250'
    x2 = add(x,'-E ^eventFilters_'+YEAR[-2:]+' ')
    if metBin != '': x2 = add(x2,'-E ^'+metBin+' -E ^'+metBin+'_trig_'+YEAR[-2:]+' ')
    else: print "\n--- NO TRIGGER APPLIED! ---\n"
    return x2

allow_unblinding = False


if __name__ == '__main__':

    torun = args.conf

    if (not allow_unblinding) and '_data' in torun and (not any([re.match(x.strip()+'$',torun) for x in ['.*appl.*','.*cr.*','3l.*_Zpeak.*']])): raise RuntimeError, 'You are trying to unblind!'


    if '2los_' in torun:
        x = base('2los')
        x = binYearChoice(x,torun,YEAR)
    
        if 'sr' in torun:
            if '_col' in torun:
                x = add(x,"-X ^mT -X ^SF ")
                if '_med' or '_high' in torun: x = add(x,"-X ^pt5sublep ")

        if 'appl' in torun:
            if '_col' in torun:
                x = add(x,"-X ^mT -X ^SF ")
                if '_med' or '_high' in torun: x = add(x,"-X ^pt5sublep ")
            x = add(x,"-X ^twoTight ")
            x = add(x,"-E ^oneNotTight ")

        if 'cr_dy' in torun:
            if '_med' in torun: x = x.replace('-E ^met200 ','-E ^met200_CR ')
            x = add(x,"-X ^ledlepPt -X ^twoTight ")
            x = add(x,"-I ^mtautau ")
            x = add(x,"-E ^CRDYlepId -E ^CRDYledlepPtIp ")

        if 'cr_tt' in torun:
            if '_med' in torun: x = add(x,'-E ^met200_CR -X ^pt5sublep ')
            x = add(x,"-X ^ledlepPt -X ^twoTight -X ^bveto -X ^mT ")
            x = add(x,"-E ^CRTTlepId -E ^CRTTledlepPt -E ^btag ")

        if 'cr_vv' in torun:
            if '_med' in torun: x = add(x,'-E ^met200_CR -X ^pt5sublep ')
            x = add(x,"-X ^ledlepPt -X ^twoTight -X ^mT ")
            x = add(x,"-E ^CRVVlepId -E ^CRVVleplepPt -E ^CRVVmT ")

        if 'cr_ss' in torun:
            if '_med' in torun: x = add(x,'-E ^met200_CR -X ^pt5sublep ')
            x = add(x,"-X ^mT ")
            x = add(x,"-I ^OS ")

    elif '3l_' in torun:
        x = base('3l')
        x = binYearChoice(x,torun,YEAR)
    
        if 'appl' in torun:
            x = add(x,"-X ^threeTight ")
            x = add(x,"-E ^oneNotTight ")

        if 'cr_wz' in torun:
            x = add(x,"-X ^minMll -X ^ZvetoTrigger -X ^ledlepPt -X ^threeTight -X ^pt5sublep ")
            x = add(x,"-E ^CRWZlepId -E ^CRWZmll ")
            x = x.replace('-E ^met200 ','-E ^met200_CR ')
            if '_min' or '_low' in torun:
                x = add(x,"-E ^CRWZPtLep_MuMu ")
                if '_min' in torun: x = x.replace('-E ^met75_trig','-E ^met75_trig_CR ')
                if '_low' in torun: x = x.replace('-E ^met125_trig','-E ^met125_trig_CR ')
            if '_med' in torun: x = add(x,"-E ^CRWZPtLep_HighMET ")

    else: raise RuntimeError("You must include either '2los' or '3l' in the command!" )


    if not args.data: x = add(x,'--xp data ')
    if args.unc: x = add(x,"--unc susy-sos-v2-clean/systsUnc.txt")
    if args.norm: x = add(x,"--sp '.*' --scaleSigToData ")

    if '_low' in torun :
        if YEAR=="2016": x = x.replace(LUMI," -l 33.2 ")
        if YEAR=="2017": x = x.replace(LUMI," -l 36.74 ")


    runIt(x,'%s'%torun)

######################################################################################
# Useful options for plotting, to be used when needed
#
#        if '_appl' in torun: x = add(x,'-I ^TT ')
#        if '_1fo' in torun:
#            x = add(x,"-A alwaystrue 1FO 'LepGood1_isLepTight+LepGood2_isLepTight==1'")
#        if '_2fo' in torun: x = add(x,"-A alwaystrue 2FO 'LepGood1_isLepTight+LepGood2_isLepTight==0'")
#        if '_relax' in torun: x = add(x,'-X ^TT ')
#        if '_extr' in torun:
#            x = x.replace('mca-2lss-mc.txt','mca-2lss-mc-sigextr.txt').replace('--showRatio --maxRatioRange 0 2','--showRatio --maxRatioRange 0 1 --ratioYLabel "S/B"')
#        if '_data' not in torun: x = add(x,'--xp data ')
#        if '_table' in torun:
#            x = x.replace('mca-2lss-mc.txt','mca-2lss-mc-table.txt')
#        if '_frdata' in torun: # Why?
#            x = promptsub(x)
#            if '_blinddata' in torun:
#                x = x.replace('mca-2lss-mc.txt','mca-2lss-mcdata.txt')
#                x = add(x,'--xp data ')
#            elif not '_data' in torun: raise RuntimeError
#            x = x.replace('mca-2lss-mcdata.txt','mca-2lss-mcdata-frdata.txt')
#            if '_table' in torun:
#                x = x.replace('mca-2lss-mcdata-frdata.txt','mca-2lss-mcdata-frdata-table.txt')
###
#            if '_leadmupt25' in torun: x = add(x,"-A 'entry point' leadmupt25 'abs(LepGood1_pdgId)==13 && LepGood1_pt>25' ")
#            if '_highMetNoBCut' in torun: x = add(x,"-A 'entry point' highMET 'met_pt>60'")
#            else: x = add(x,"-E ^1B ")
