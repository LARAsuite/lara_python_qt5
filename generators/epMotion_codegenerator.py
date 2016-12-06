#!/usr/bin/env python
# -*- coding: utf-8 -*-

#_____________________________________________________________________________
#
# PROJECT: LARA
# CLASS: epmotion_code_generator
# FILENAME: epmotion_code_generator.py
#
# CATEGORY:
#
# AUTHOR: mark doerr
# EMAIL: mark@ismeralda.org
#
# VERSION: 0.0.3
#
# CREATION_DATE: 2015/03/24
# LASTMODIFICATION_DATE: 2016/06/01
#
# BRIEF_DESCRIPTION: Code Generator for Eppendorf EpMotion
# DETAILED_DESCRIPTION: 
#          position table:         A2:151, A3:152, A4:157, 
#                          B1:156, B2:153, B3:154, B4:158, 
#                          C1:160, C2:161, C3:162, C4:159 
# TODO: default volumes for oil and mastermix
# ____________________________________________________________________________
#
#   Copyright:
#   This program is free software; you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation; either version 2 of the License, or
#   (at your option) any later version.
#
#   This file is provided "AS IS" with NO WARRANTY OF ANY KIND,
#   INCLUDING THE WARRANTIES OF DESIGN, MERCHANTABILITY AND FITNESS FOR
#   A PARTICULAR PURPOSE.
#
#   For further Information see COPYING file that comes with this distribution.
#_______________________________________________________________________________

import sys
import logging
import datetime

import singledispatch  # will be included in python 3.4 functools library; for python < 3.3 plese use pip install singledispatch

import lara_process as lap
import lara_material as lam

from lara_codegenerator import LA_CodeGenerator

class LA_GenerateEPMotionCode(LA_CodeGenerator):
    """Code generator class for generating epMotion code using the visitor pattern"""
    #experiment, automation_sys, container_db, container_location_db
    def __init__(self, subprocess_steps, experiment=None  ):
        super(LA_GenerateEPMotionCode, self).__init__(subprocess_steps)

        #~ logging.debug("in the epi gen %s" % subprocess_steps )
        
        self.ep_process = []
        self.experiment = experiment
    
        #~ self.automation_sys = automation_sys
        #~ self.container_db = container_db
        #~ self.container_location_db = container_location_db
        
        self.EPMotion_proc_filename = experiment.name()
        
        # material workaround until lara material is fixed        
        self.material_dict = {"TS_50":("./top/dws/tools/TS_50", 4),
                              "tip50":("./top/dws/tips/tip50", 4),
                              "Adap_40":("./top/dws/adapter/height/Adap_40", 16),
                              "Rack_1_5ml":("./top/dws/trth/Rack_1_5ml", 512),
                              "GR_MTP_390orig": ("./top/dws/plates/mtp96/GR_MTP_390orig", 8),
                              "GR_MTP_120_1": ("./top/dws/plates/mtp384/GR_MTP_120_1", 8),
                              "GR_MTP_120_1HEAT": ("./top/dws/plates/mtp384/GR_MTP_120_1HEAT", 8) }
                              
        # material workaround until lara material is fixed        
        self.liquid_dict =   {"Water":"./top/dws/liquids/Water",
                              "Glycerol":"./top/dws/liquids/Glycerol"}

        self.initDispatcher()
        
        # parse the process steps

        self.traverse()             

        # finally write everything into a file
        self.writeEPMotionFile()
        
    def initDispatcher(self):
        self.generate = singledispatch.singledispatch(self.generate)
        self.generate.register(lap.BeginSubProcess, self.genBeginSubProcess)
        self.generate.register(lap.EndSubProcess, self.genEndSubProcess)
        self.generate.register(lap.PreRunMethod, self.genPreRunMethod)
        self.generate.register(lap.PostRunMethod, self.genPostRunMethod)
        self.generate.register(lap.SetSampleNum, self.genNumSamples)
        self.generate.register(lap.MovePlate, self.genPlacePlate)
        self.generate.register(lap.SetTemperature, self.genSetTemperature)
        self.generate.register(lap.ThermoMix, self.genThermoMix)
        self.generate.register(lap.Incubate, self.genIncubate)
        self.generate.register(lap.UserAction, self.genUserAction)
        self.generate.register(lap.Comment, self.genComment)
        self.generate.register(lap.LiquidTransfer, self.genLiquidTransfer)
        self.generate.register(lap.LoadTips, self.genLoadTips)
        self.generate.register(lap.UnloadTips, self.genUnloadTips)
           
    def generate(self,item):
        logging.warning("epmotion cg: generic item: %s" % item)
        #raise TypeError("Type not supported.")
        
    def genBeginSubProcess(self, process_step):
        self.subprocess_name = process_step.name()
        
        self.ep_process_head = ( "[Properties]\n"
                                   "Name={name}\n"
                                   "Comment=\n"
                                   "DWS-ability=0x0001C002\n"   # DWS-ability=0x0000FF06
                                   "\n[Version]\n"
                                   "Name={name}.dws\n"
                                   "Struktur=PrgStruc 0.21\n\n".format(name=self.EPMotion_proc_filename) )
               
    def genEndSubProcess(self, process_step):
        self.ep_process += [(  "OpcodeStr=End\n"
                               "Opcode=129\n") ]

    def genPlacePlate(self,process_step):
        container_type = process_step.containerType()
        
        if ( process_step.isStatic() == "1"):
            self.ep_process += [( "OpcodeStr=Place it\n"
                                 "Opcode=115\n"
                                 "Bezeichner=\n"
                                 "MatDatei={cont_mat_file}\n"
                                 "MatName={cont_type}\n"
                                 "BehaelterName={cont_name}\n"
                                 "EnumMatType={cont_mat_num}\n"
                                 "EnumSlotNr={cont_pos}\n"
                                 "Stapelindex={cont_staple_index}\n"
                                 "RackLevelSensor=0\n"
                                 "RackTemperatur=0\n".format(cont_mat_file=self.material_dict[container_type][0],
                                                             cont_type = container_type,
                                                             cont_name=process_step.containerList()[0],
                                                             cont_mat_num=self.material_dict[container_type][1],
                                                             cont_pos=process_step.platePosition(),
                                                             cont_staple_index=process_step.stapleIndex() ))]
        else :
            self.ep_process += [( "OpcodeStr=Transport\n"
                                  "Opcode=107\n"
                                  "Bezeichner=\n"
                                  "TransWhom={cont_name}\n"
                                  "TransToPos={cont_pos}\n".format( cont_name=process_step.containerList()[0],
                                                                    cont_pos=process_step.platePosition() ))]
                                                                                                                                 
    def genPreRunMethod(self,process_step):
        self.ep_process += [( "OpcodeStr=PreRun\n"
                              "Opcode=116\n"
                              "Bezeichner=\n"
                              ) ]
                              
    def genNumSamples(self,process_step):
        self.ep_process += [( "OpcodeStr=NumberOfSamples\n"
                              "Opcode=118\n"
                              "Bezeichner=\n"
                              "Fest=1\n"
                              "festeProbenzahl={sample_num}\n"
                              "maxProbenzahl=0\n".format( sample_num=process_step.sampleNum() ) )]                          
                              
    def genPostRunMethod(self,process_step):
        self.ep_process += [( "OpcodeStr=PostRun\n"
                              "Opcode=117\n"
                              "Bezeichner=\n") ]
                             
    def genLiquidTransfer(self,process_step):
        logging.info("--------- !!!!!  correct pattern ....")
        self.ep_process += [( "OpcodeStr=SampleTransfer\n"
                              "Opcode=101\n"
                              "Bezeichner=\n"
                              "ToolDatei=./top/dws/tools/TS_50\n"
                              "ToolName=TS_50\n"
                              "Filter=0\n"
                              "TransferVolumenNanoliter={volume}\n"
                              "TransferVolumenUnit=0\n"
                              "EnumDosierart=0\n"
                              "Source1={source_plate}\n"
                              "Destination1={target_plate}\n"
                              "LiqDatei={liquid_file}\n"
                              "LiqName={liquid}\n"
                              "EditDosPar=0\n"
                              "SrcSimple={pipetting_from_bottom}\n"     # pipetting from bottom: 1 ; from top: 0   
                              "DesSimple=0\n"
                              "Elution=0\n"
                              "MixBefore={mix_sample_before}\n"
                              "MixBeforeTumSpeed={mix_speed}\n"
                              "MixBeforeVolumenNanoliter={mix_volume}\n"
                              "MixBeforeVolumenUnit=0\n"
                              "MixBeforeNoOfCycles={mix_num_cycles}\n"
                              "MixBeforeFixedHeight=0\n"
                              "MixBeforeFixAb=0\n"
                              "MixBeforeFixAuf=0\n"
                              "MixAfter={mix_sample_after}\n"
                              "MixAfterFixAb=0\n"
                              "MixAfterTumSpeed={mix_speed}\n"
                              "MixAfterVolumenNanoliter={mix_volume}\n"
                              "MixAfterVolumenUnit=0\n"
                              "MixAfterNoOfCycles={mix_num_cycles}\n"
                              "MixAfterFixedHeight=0\n"
                              "MixAfterFixAuf=0\n"
                              "EnumEjectTips={change_tips}\n"           # 4 : keep tips 
                              "EjectAnzAufnahmen=0\n"
                              "IrregularPattern=0\n"
                              "IrregularSrcPat=0\n"
                              "IrregularDesPat=0\n"
                              "StandardPattern=0\n"
                              "EnumStdRichtung=9\n"
                              "EnumMusterTyp=2\n"
                              "Source_Pat_Type=0\n"
                              "Source_Pat_Anz=1\n"
                              "Source_Pat_AnzDup=1\n"
                              "Source_Pat_RasterX=12\n"
                              "Source_Pat_RasterY=8\n"
                              "Source_Pat_Kanalzahl=1\n"
                              "Source_Pat_AnzRacks=1\n"
                              "Source_Pat_AnzSpalten=12\n"
                              "Source_Pat_AnzZeilen=8\n"
                              "Source_Pat_T1=1\n"
                              "Source_Pat_S1={src_column_pos}\n"
                              "Source_Pat_Z1={src_row_pos}\n"
                              "Source_Pat_Vorhanden=1\n"
                              "Destination_Pat_Type=0\n"
                              "Destination_Pat_Anz=1\n"
                              "Destination_Pat_AnzDup=1\n"
                              "Destination_Pat_RasterX=12\n"
                              "Destination_Pat_RasterY=8\n"
                              "Destination_Pat_Kanalzahl=1\n"
                              "Destination_Pat_AnzRacks=1\n"
                              "Destination_Pat_AnzSpalten=12\n"
                              "Destination_Pat_AnzZeilen=8\n"
                              "Destination_Pat_T1=1\n"
                              "Destination_Pat_S1={tar_column_pos}\n"
                              "Destination_Pat_Z1={tar_row_pos}\n"
                              "Destination_Pat_Vorhanden=1\n".format(volume=process_step.volume()*1000, liquid=process_step.liquid(), 
                                                                     liquid_file=self.liquid_dict[process_step.liquid()],
                                                                     pipetting_from_bottom=1,
                                                                     mix_sample_before=process_step.mixSampleBefore(),
                                                                     mix_sample_after=process_step.mixSampleAfter(),
                                                                     mix_speed=process_step.mixSpeed(), mix_volume = process_step.mixVolume(),
                                                                     mix_num_cycles=process_step.mixNumCycle(), 
                                                                     change_tips=3,  
                                                                     source_plate=process_step.srcPlatePos(), target_plate=process_step.tarPlatePos(),
                                                                     src_column_pos=process_step.srcColPos(), src_row_pos=process_step.srcRowPos(),
                                                                     tar_column_pos=process_step.tarColPos(), tar_row_pos=process_step.tarRowPos()  ) )]

    def genSetTemperature(self,process_step):
        self.ep_process += [( "OpcodeStr=Temperature\n"
                              "Opcode=108\n"
                              "Bezeichner=\n"
                              "TempPos={cont_pos}\n"
                              "Temperature={temperature}\n"
                              "TempOn=1\n"
                              "TempHold=1\n".format(cont_pos=process_step.platePosition(), temperature=int(process_step.Temperature()) )) ]
                              

    def genThermoMix(self,process_step):
        self.ep_process += [( "OpcodeStr=Thermomixer\n"
                              "Opcode=123\n"
                              "Bezeichner=\n"
                              "WithTemplate=0\n"
                              "TemplateDatei=top/dws/tmx/\n"
                              "TemplateName=TALE37temp\n"
                              "EditTempPar=0\n"
                              "SpeedOn=0\n"
                              "MixSpeed=500\n"
                              "MixTimeMinute=1\n"
                              "MixTimeSecond=0\n"
                              "TempOn=1\n"
                              "Temperature={temperature}\n"
                              "TempHold=0\n".format(temperature=int(process_step.Temperature()) )) ]

    def genIncubate(self,process_step):
        duration_sec = process_step.incubationDuration()
        duration_min = duration_sec / 60
        duration_sec = duration_sec - duration_min * 60
        
        self.ep_process += [( "OpcodeStr=Wait\n"
                              "Opcode=112\n"
                              "Bezeichner=\n"
                              "WaitMinute={duration_min}\n"
                              "WaitSekunde={duration_sec}\n"
                              "WaitTemp=0\n"
                              "WaitTempPos={cont_pos}\n"
                              "WaitCycler=0\n".format(cont_pos=process_step.platePosition(), 
                                                      duration_min=str(duration_min), 
                                                      duration_sec=str(duration_sec) )) ] 

    def genComment(self,process_step):
        self.ep_process += [( "OpcodeStr=Comment\n"
                              "Opcode=113\n"
                              "Bezeichner={comment}\n".format(comment=process_step.comment() )) ]

    def genUserAction(self,process_step):
        self.ep_process += [( "OpcodeStr=UserIntervention\n"
                              "Opcode=114\n"
                              "Bezeichner={message}\n"
                              "Alarm=1\n".format(message=process_step.message() )) ]

    def genLoadTips(self,process_step):
        logging.debug("ep -- loading tips") 
        
    def genUnloadTips(self,process_step):
        logging.debug("ep -- unloading tips")
                
    def writeEPMotionFile(self):
        ep_output_filename = self.EPMotion_proc_filename + ".dws"
        with open(ep_output_filename, 'w') as ep_outfile:
            ep_outfile.write(self.ep_process_head)
            i = 1
            for sp_steps in self.ep_process:
                ep_outfile.write("[%03d]\n%s\n" %(i,sp_steps) ) # adding step counter
                i += 1
        
        #~ except IOError:
            #~ logging.Error("Cannot write epMotion outputfile %s; Error: !!!" % (ep_output_filename))
