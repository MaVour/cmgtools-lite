#!/bin/bash

if [[ "$HOSTNAME" == "cmsco01.cern.ch" ]]; then
    T="/data1/peruzzi/TREES_76X_200216_jecV1M2_skimOnlyMC_reclv8";
    J=14;
else
    T="/afs/cern.ch/work/p/peruzzi/tthtrees/TREES_76X_200216_jecV1M2";
    J=4;
fi

if [[ "X$1" == "X" ]]; then echo "Provide output directory name!"; exit; fi
OUTNAME=$1; shift;
if [[ "X$1" == "X" ]]; then echo "Provide luminosity!"; exit; fi
LUMI="$1"; shift
echo "Normalizing to ${LUMI}/fb";
OPTIONS=" -P $T --tree treeProducerSusyMultilepton --s2v -j $J -l ${LUMI} -f --asimov "
test -d cards/$OUTNAME || mkdir -p cards/$OUTNAME
OPTIONS="${OPTIONS} --od cards/$OUTNAME ";

SYSTS="ttH-multilepton/systsEnv.txt"
BLoose=" -E BLoose "
BTight=" -E BTight "
ZeroTau=" -E 0tau "
OneTau=" -E 1tau "

OPTIONS="${OPTIONS} --Fs {P}/2_recleaner_v8_b1E2 --Fs {P}/4_kinMVA_trainFeb23_v0 --Fs {P}/5_eventBTagRWT_onlyJets_v1"
OPTIONS="${OPTIONS} --mcc ttH-multilepton/lepchoice-ttH-FO.txt --mcc ttH-multilepton/ttH_2lss3l_triggerdefs.txt --neg" # neg necessary for subsequent rebin
OPTIONS="${OPTIONS} --xp data" # safety!

FUNCTION_2L="kinMVA_2lss_ttV:kinMVA_2lss_ttbar 20,-1,1,20,-1,1"
FUNCTION_3L="kinMVA_3l_ttV:kinMVA_3l_ttbar 20,-1,1,20,-1,1"

if [[ "$1" == "" || "$1" == "2lss" ]]; then
    OPT_2L="${OPTIONS} -W puw(nTrueInt)*leptonSF_ttH(LepGood_pdgId[iF_Recl[0]],LepGood_pt[iF_Recl[0]],LepGood_eta[iF_Recl[0]],2)*leptonSF_ttH(LepGood_pdgId[iF_Recl[1]],LepGood_pt[iF_Recl[1]],LepGood_eta[iF_Recl[1]],2)*triggerSF_ttH(LepGood_pdgId[iF_Recl[0]],LepGood_pt[iF_Recl[0]],LepGood_pdgId[iF_Recl[1]],LepGood_pt[iF_Recl[1]],2)*eventBTagSF"
    POS=" -A alwaystrue positive LepGood1_charge>0 "
    NEG=" -A alwaystrue negative LepGood1_charge<0 "

    for X in mm ee em; do 
        echo "2lss_${X}";
	FLAV=" -E ${X} "
	if [[ "${X}" == "ee" ]]; then
	    python makeShapeCards.py --2d-binning-function 6:ttH_MVAto1D_6_2lss_Marco ttH-multilepton/mca-2lss-mcdata-frdata.txt ttH-multilepton/2lss_tight.txt ${FUNCTION_2L} $SYSTS $OPT_2L -o 2lss_${X}_0tau_pos $POS $FLAV $ZeroTau;
            python makeShapeCards.py --2d-binning-function 6:ttH_MVAto1D_6_2lss_Marco ttH-multilepton/mca-2lss-mcdata-frdata.txt ttH-multilepton/2lss_tight.txt ${FUNCTION_2L} $SYSTS $OPT_2L -o 2lss_${X}_0tau_neg $NEG $FLAV $ZeroTau;
	else
	    python makeShapeCards.py --2d-binning-function 6:ttH_MVAto1D_6_2lss_Marco ttH-multilepton/mca-2lss-mcdata-frdata.txt ttH-multilepton/2lss_tight.txt ${FUNCTION_2L} $SYSTS $OPT_2L -o 2lss_${X}_0tau_bl_pos $POS $BLoose $FLAV $ZeroTau;
            python makeShapeCards.py --2d-binning-function 6:ttH_MVAto1D_6_2lss_Marco ttH-multilepton/mca-2lss-mcdata-frdata.txt ttH-multilepton/2lss_tight.txt ${FUNCTION_2L} $SYSTS $OPT_2L -o 2lss_${X}_0tau_bl_neg $NEG $BLoose $FLAV $ZeroTau;
            python makeShapeCards.py --2d-binning-function 6:ttH_MVAto1D_6_2lss_Marco ttH-multilepton/mca-2lss-mcdata-frdata.txt ttH-multilepton/2lss_tight.txt ${FUNCTION_2L} $SYSTS $OPT_2L -o 2lss_${X}_0tau_bt_pos $POS $BTight $FLAV $ZeroTau;
            python makeShapeCards.py --2d-binning-function 6:ttH_MVAto1D_6_2lss_Marco ttH-multilepton/mca-2lss-mcdata-frdata.txt ttH-multilepton/2lss_tight.txt ${FUNCTION_2L} $SYSTS $OPT_2L -o 2lss_${X}_0tau_bt_neg $NEG $BTight $FLAV $ZeroTau;
	fi
    done

    python makeShapeCards.py --2d-binning-function 6:ttH_MVAto1D_6_2lss_Marco ttH-multilepton/mca-2lss-mcdata-frdata.txt ttH-multilepton/2lss_tight.txt ${FUNCTION_2L} $SYSTS $OPT_2L -o 2lss_1tau $OneTau;

    echo "Done at $(date)"

fi

if [[ "$1" == "" || "$1" == "3l" ]]; then
    OPT_3L="${OPTIONS} -W puw(nTrueInt)*leptonSF_ttH(LepGood_pdgId[iF_Recl[0]],LepGood_pt[iF_Recl[0]],LepGood_eta[iF_Recl[0]],3)*leptonSF_ttH(LepGood_pdgId[iF_Recl[1]],LepGood_pt[iF_Recl[1]],LepGood_eta[iF_Recl[1]],3)*leptonSF_ttH(LepGood_pdgId[iF_Recl[2]],LepGood_pt[iF_Recl[2]],LepGood_eta[iF_Recl[2]],3)*triggerSF_ttH(LepGood_pdgId[iF_Recl[0]],LepGood_pt[iF_Recl[0]],LepGood_pdgId[iF_Recl[1]],LepGood_pt[iF_Recl[1]],3)*eventBTagSF"
    POS=" -A alwaystrue positive (LepGood1_charge+LepGood2_charge+LepGood3_charge)>0 "
    NEG=" -A alwaystrue negative (LepGood1_charge+LepGood2_charge+LepGood3_charge)<0 "

    echo "3l";
    python makeShapeCards.py --2d-binning-function 3:ttH_MVAto1D_3_3l_Marco ttH-multilepton/mca-3l-mcdata-frdata.txt ttH-multilepton/3l_tight.txt ${FUNCTION_3L} $SYSTS $OPT_3L -o 3l_bl_pos $POS $BLoose;
    python makeShapeCards.py --2d-binning-function 3:ttH_MVAto1D_3_3l_Marco ttH-multilepton/mca-3l-mcdata-frdata.txt ttH-multilepton/3l_tight.txt ${FUNCTION_3L} $SYSTS $OPT_3L -o 3l_bl_neg $NEG $BLoose;
    python makeShapeCards.py --2d-binning-function 3:ttH_MVAto1D_3_3l_Marco ttH-multilepton/mca-3l-mcdata-frdata.txt ttH-multilepton/3l_tight.txt ${FUNCTION_3L} $SYSTS $OPT_3L -o 3l_bt_pos $POS $BTight;
    python makeShapeCards.py --2d-binning-function 3:ttH_MVAto1D_3_3l_Marco ttH-multilepton/mca-3l-mcdata-frdata.txt ttH-multilepton/3l_tight.txt ${FUNCTION_3L} $SYSTS $OPT_3L -o 3l_bt_neg $NEG $BTight;

   echo "Done at $(date)"
fi

