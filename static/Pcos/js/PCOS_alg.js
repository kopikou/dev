function CheckPCOS(	ethnicity_,
					periods_,
					type_menstrual_disorders_1_,
					type_menstrual_disorders_3_,
					type_menstrual_disorders_4_,
					min_menstrual_,
					max_menstrual_,
					sum_physician_,
					day_of_begin_,
					right_volume_total_,
					right_follicle_total_,
					diameter_right_total_,
					left_volume_total_,
					left_follicle_total_,
					diameter_left_total_,
					value_testosteron_,
					value_shbg_,
					value_dheas_,
					value_tsh_,
					day_mens_prl_,
					value_17hp_,
					value_prl_,
					value_testosteron_max_,
					value_IFA_max_,
					value_dheas_max_,
					value_tsh_min_,
					value_tsh_max_,
					value_17hp_max_1_,
					value_prl_max_1_,
					value_prl_max_2_,
					age_visit1_,
					inform_consent_,
					comply_all_study_,
					female_age_,
					current_preg_lact_,
					history_hysterectomy_,
					risk_no_compliance_,
					unwillingness_,
					medicince_listed_now___10_,
					medicince_listed_3month___10_,
					pnya_
					)
{
		
		OA=null 	
		PCOM=null	 
		H=null	 
		included=0
		
		if (inform_consent_!=null && comply_all_study_!=null && female_age_!=null && current_preg_lact_!=null && history_hysterectomy_!=null && risk_no_compliance_!=null && unwillingness_!=null && medicince_listed_now___10_!=null && medicince_listed_3month___10_!=null)
		{
			if (inform_consent_==true && comply_all_study_==true && female_age_==true && current_preg_lact_==false && history_hysterectomy_==false && risk_no_compliance_==false && unwillingness_==false&& medicince_listed_now___10_==true && medicince_listed_3month___10_==true)
				{included=1 }
		}

		if (included==1) 
		{
			if (periods_!=null)
			{ 
				if (periods_=='2' || periods_=='3') 
				{
					if (type_menstrual_disorders_1_=='2' || type_menstrual_disorders_1_=='3' ||
				      type_menstrual_disorders_3_==true || type_menstrual_disorders_4_==true)
					{
						OA=1
					}
				}
 			}
			if (min_menstrual_!=null)
			{
				if (min_menstrual_<21) 
				{
					OA=1
				} 
			}
			if (max_menstrual_!=null)
			{
				if (max_menstrual_>35) 
				{
					OA=1
				} 
			}
			if (periods_!=null)
			{
				if (periods_=='1') 
				{
					if (type_menstrual_disorders_1_=='1' &&  type_menstrual_disorders_3_==false && type_menstrual_disorders_4_==false)
					{
						if (min_menstrual_!=null)
						{
							if (min_menstrual_>=21) 
							{
								if (max_menstrual_!=null)
								{
									if (max_menstrual_<=35) 
									{
										OA=0
									} 
								}
							} 
						}
					}
			
				}
 			}
 			
			//***************************************************
			PCOM_right=991
			PCOM_left=991
			right_volume_total=0
			right_follicle_total=0
			diameter_right_total=0

			if (right_volume_total_!=null)
			{
		  	right_volume_total=right_volume_total_
			}

			if (right_follicle_total_!=null)
			{
		  	right_follicle_total=right_follicle_total_
			}

			if (diameter_right_total_!=null)
			{
		  	diameter_right_total=diameter_right_total_
			}

			if (diameter_right_total!=null)
			{
				if (right_volume_total>=10 || right_follicle_total>=12) 
				{
					if (diameter_right_total<=9) 
					{   
						PCOM_right=1
					}
					else
					{   
				  	PCOM_right=991
				  }
				}
 			}
 			
			if (right_volume_total!=null && right_follicle_total==null)
			{
		  	add_text="ошибка right 1"
			}
			if (right_volume_total==null && right_follicle_total!=null)
			{
		  	add_text="ошибка right 1" 
			}
			if (right_volume_total==null  && right_follicle_total==null && diameter_right_total!=null)
			{
				add_text="ошибка right 3"
			} 

			left_volume_total=0
			left_follicle_total=0
			diameter_left_total=0

			if (left_volume_total_!=null)
			{
		  	left_volume_total=left_volume_total_
			}
			if (left_follicle_total_!=null)
			{
		  	left_follicle_total=left_follicle_total_
			}
			if (diameter_left_total_!=null)
			{
		  	diameter_left_total=diameter_left_total_
			}

			if (diameter_left_total!=null)
			{
				if (left_volume_total>=10 || left_follicle_total>=12) 
				{
					if (diameter_left_total<=9) 
					{   
						PCOM_left=1
					}
					else
					{   
				  	PCOM_left=991
				  }
				}
 			}
 			
			if (left_volume_total!=null && left_follicle_total==null)
			{
		  	add_text="ошибка left 1"
			}
			if (left_volume_total==null && left_follicle_total!=null)
			{
		  	add_text="ошибка left 2" 
			}
			if (left_volume_total==null && left_follicle_total==null && diameter_left_total!=null)
			{
		  	add_text="ошибка left 3" 
			}
			if (PCOM_right==1 || PCOM_left==1)
			{
				PCOM=1
			}	
			if (right_volume_total!=null && right_follicle_total!=null && diameter_right_total!=null)
			{
				if (right_volume_total<10 && right_follicle_total<12) 
				{
					if (diameter_right_total<=9) 
					{   
						PCOM_right=0
					}
			  	if (diameter_right_total>9) 
			  	{   
			    	PCOM_right=991
			  	}
				}
			}
			if (left_volume_total!=null && left_follicle_total!=null && diameter_left_total!=null)
			{
				if (left_volume_total<10 && left_follicle_total<12) 
				{
					if (diameter_left_total<=9) 
					{   
						PCOM_left=0
					}
			  	if (diameter_left_total>9) 
			  	{   
			    	PCOM_left=991
			  	}
				}
 			}
			if ((PCOM_right==0 && PCOM_left==0) || (PCOM_right==991 && PCOM_left==0) || (PCOM_right==0 &&PCOM_left==991))
			{
		  	PCOM=0
			}	
		
			//************************************************************************************
			if (ethnicity_==null)			
			{
				krit_testosteron=67.34
				krit_IFA=5.42
			}
			else
			{
				race=ethnicity_
				if (race==1)
				{
					krit_testosteron=73.9
					krit_IFA=6.9
				}
				if (race==2||race==3)
				{
					krit_testosteron=41.03
					krit_IFA=2.92
				}
			}
			if (value_testosteron_max_!=null){krit_testosteron=value_testosteron_max_ }
			if (value_IFA_max_!=null){krit_IFA=value_testosteron_max_ }
			
			
    	H_sum_ph=null
    	H_test=null
    	H_IFA=null
    	H_dheas=null
		
			if (sum_physician_!=null)			
			{
				sum_physician=sum_physician_
				if (sum_physician>4)
				{
					H=1 
					H_sum_ph=1
				}
				if (sum_physician<=4)
				{
				  H_sum_ph=0
				}
			}
			testosteron=0
			testosteron_ng_dl=null
			IFA=null
			if (value_testosteron_!=null)			
			{
				testosteron=value_testosteron_/1000*3.467
				testosteron_ng_dl=value_testosteron_/10
				if (testosteron_ng_dl>krit_testosteron)
				{
					H=1 
					
					H_test=1
				}
				if (testosteron_ng_dl<=krit_testosteron)
				{
				  H_test=0
				}
			}
			else
			{
				testosteron=null
			}
			if (value_shbg_!=null && testosteron>0)
			{
				IFA=testosteron/value_shbg_*100
				if (IFA>krit_IFA)
				{
					H=1 
					H_IFA=1
				}
				if (IFA<=krit_IFA)
				{
				
				  H_IFA=0
				}
			}
			else
			{
				IFA=null
			}
			
			value_dheas=0
			if (value_dheas_!=null)			
			{
				value_dheas=value_dheas_
				if (value_dheas>value_dheas_max_)
				{
					H=1 
					H_dheas=1
				}
				if (value_dheas<=value_dheas_max_)
				{
				  H_dheas=0
				}
			}
		
			if (sum_physician_!=null && testosteron_ng_dl!=null && IFA!=null && value_dheas_!=null)
			{
				if (sum_physician<=4 && testosteron_ng_dl<=krit_testosteron && IFA<=krit_IFA && value_dheas<=value_dheas_max_)
					{
						H=0
					}
			}
			
			
			//****************************************************

			PH=null
			PCOS=null
			if (OA!=null && H!=null && PCOM!=null)
			{
				if (OA==1 && H==1 && PCOM==1)
				{
					PH="A"
				}
				if (OA==1 && H==1 && PCOM==0)
				{
					PH="B"
				}
				if (OA==0 && H==1 && PCOM==1)
				{
					PH="C"
				}
				if (OA==1 && H==0 && PCOM==1)
				{
					PH="D"
				}
				if (OA==0 && H==0 && PCOM==0)
				{
					PCOS=0
				}
			}

			if (OA==null) {OA__=0} else {OA__=OA}
			if (H==null)  {H__=0}  else {H__=H}
			if (PCOM==null) {PCOM__=0} else { if (PCOM==1) {PCOM__=1} else {PCOM__=0}}
			if (OA__+H__+PCOM__==2 && PH==null) {PH=0}
			if (PH!=null)
			{
				PCOS=1
			}
			
			//data1[i,"Phenotype"]=PH
			//data1[i,"PCOS"]=PCOS
			//*****************************************************
			F_PCOS=null
			F_Phenotype=null
			ex_prl=null
			ex_tsh=null
			ex_17ph=null
			ex_pnya=null
			ex=null
			grey=0
			if (value_tsh_!=null)	
			{
				tsh=value_tsh_
				if (tsh>value_tsh_max_ || tsh<value_tsh_min_)
				{
					ex_tsh=1 
				}
				if (tsh>=value_tsh_min_ && tsh<=value_tsh_max_)
				{
			  	ex_tsh=0 
				}
			}
			ex_pnya=0
			if (pnya_!=null)	
			{
				pnya=pnya_
				if (pnya==true)
				{
					ex_pnya=1 
				}
				if (pnya==false)
				{
					ex_pnya=0 
				}
			}
			if (day_mens_prl_!=null && value_17hp_!=null && value_prl_!=null)
			{
				if (day_mens_prl_<=9)
				{	
			 	if (value_17hp_>value_17hp_max_1_	)
			  	{
			    	ex_17ph=1
			  	}  
			  if (value_17hp_<=	value_17hp_max_1_	)
			  	{
			    	ex_17ph=0
			  	}  
			  	if (value_prl_>	value_prl_max_1_)
			  	{
			    	ex_prl=1
			  	}  
			  	if (value_prl_<=	value_prl_max_1_)
			  	{
			    	ex_prl=0
			  	}  
				}

		  	if (day_mens_prl_>9)
		  	{
		    	ex_17ph=0
		  	}
		  	if (day_mens_prl_>9 && day_mens_prl_<=35)
		  	{
		    	if (value_prl_>value_prl_max_2_	)
		    	{
		      	ex_prl=1
		    	}  
		    	if (value_prl_<=value_prl_max_2_	)
		    	{
		      	ex_prl=0
		    	}  
		  	}
		  	if (day_mens_prl_>35)
		  	{
		    	if (value_prl_>	value_prl_max_1_)
		    	{
		      	ex_prl=1
		    	}  
		    	if (value_prl_<=	value_prl_max_1_)
		   	 	{
		      	ex_prl=0
		    	}  
		  	}
			}
			if (day_mens_prl_==null && value_prl_!=null)
			{
		  	ex_17ph=0
		  	if (value_prl_>	value_prl_max_1_)
		  	{
		   		ex_prl=1
		  	}  
		  	if (value_prl_<=	value_prl_max_1_)
		  	{
		    	ex_prl=0
		  	}  
			}
			if (ex_pnya!=null)
			{
				if (ex_pnya==1)
			  {
			    ex=1
			  }
			}  

			if (ex_tsh!=null)
			{
		  	if (ex_tsh==1)
		  	{
		    	ex=1
		  	}
			}  
			if (ex_17ph!=null)
			{
		  	if (ex_17ph==1)
		  	{
		    	ex=1
		  	} 
			}  
			if (ex_prl!=null)
			{
		  	if (ex_prl==1)
		  	{
		    	ex=1
		  	} 
			}  
			
			if (ex_tsh!=null && ex_17ph!=null && ex_prl!=null && ex_pnya!=null)
			{
		  	if (ex_tsh==0 && ex_17ph==0 && ex_prl==0 && ex_pnya==0)
		  	{
		    	ex=0
		  	}
			}

		  if (ex!=null)
		  {
			  if (ex==1)
			  {
				  F_PCOS=null
				  F_Phenotype=null
			  }
			  if (ex==0)
			  {
			    F_PCOS=PCOS
				  F_Phenotype=PH
			  }
		  }
		  else
		  {
			  F_PCOS=null
			  F_Phenotype=null
		  }
		   
			if (OA__+H__+PCOM__==1)
			{	
				grey=1
				F_PCOS=0	
			}

  		//*************************************************************
	}	//included
	
		PCOS_text="Дата начала диспансерного наблюдения "+day_of_begin_+". "
		if (F_PCOS==1)
		{	
			PCOS_text=PCOS_text+"Заключительный (уточненный) диагноз: синдром поликистоза яичников (МКБ:Е28.2). "
			if (F_Phenotype!=null && F_Phenotype!=0)
			{
				PCOS_text=PCOS_text+"Фенотип СПКЯ (согласно критериям Rotterdam 2003): "+F_Phenotype+". "
				if (OA==1)
				{	
					PCOS_text=PCOS_text+"Олигоановуляция. "
				}
				
				if (PCOM==1)
				{
					PCOS_text=PCOS_text+"Поликистозная структура яичников или УЗИ-признаки поликистозных яичников (ПКЯ). "
					if (PCOM_right==1)
					{  
						PCOS_text=PCOS_text+"(Количество антральных фолликулов в правом яичнике: "+ right_follicle_total+" объем правого яичника: "+right_volume_total +"). "
					}
					if (PCOM_left==1)
					{  
						PCOS_text=PCOS_text+"(Количество антральных фолликулов в левом яичнике "+ left_follicle_total+" объем левого яичника: "+ left_volume_total+"). "
					}
				}
				if (H==1)
				{
					PCOS_text=PCOS_text+"Гиперандрогенизм. "
				}
			}
		}
		if (F_PCOS==0)
		{	
			if (grey==0)
			{
				PCOS_text=PCOS_text+"Заключительный (уточненный) диагноз: синдром поликистоза яичников не подтвержден. "
			}
			if (grey==1)
			{
				PCOS_text=PCOS_text+"Заключительный (уточненный) диагноз: синдром поликистоза яичников не подтвержден, при этом присутствуют: "
				if (OA==1)
				{
					PCOS_text=PCOS_text+"олигоановуляция; "
				}
				if (PCOM==1)
				{
					PCOS_text=PCOS_text+"поликистозная структура яичников или УЗИ-признаки поликистозных яичников (ПКЯ); "
				}
				if (H==1)
				{
					PCOS_text=PCOS_text+"гиперандрогенизм - "
					if (H_sum_ph==1)
					{
						PCOS_text=PCOS_text+"гирсутизм; "
					}
					if (H_test==1 || H_IFA==1 || H_dheas==1)
					{
						PCOS_text=PCOS_text+"избыток андрогенов ("
						
						if (H_test==1)
						{
							PCOS_text=PCOS_text+"уровень тестостерона"
							if (H_IFA==1 || H_dheas==1)
							{
								PCOS_text=PCOS_text+", "
							}
						}
						if (H_IFA==1)
						{
							PCOS_text=PCOS_text+"индексы свободных андрогенов"
							if (H_dheas==1)
							{
								PCOS_text=PCOS_text+", "
							}

						}
						if (H_dheas==1)
						{
							PCOS_text=PCOS_text+"ДГЭАС "
						}
						PCOS_text=PCOS_text+") выше нормативных значений. "
					}	
				}

			}
		
			if (grey==null)
			{
					PCOS_text=PCOS_text+"Заключительный (уточненный) диагноз: синдром поликистоза яичников не подтвержден, при этом недостаточно данных для диагностики 'серой зоны': "+OA+H+PCOM
				if (OA==null)
				{
					PCOS_text=PCOS_text+"нет данных по OA; "
				}
				if (PCOM==null)
				{
					PCOS_text=PCOS_text+"нет данных по УЗИ; "
				}
				if (H==null)
				{
					PCOS_text=PCOS_text+"нет данных по лабораторным исследованиям; "
				}


			}
		}
		if (F_PCOS==null && ex==null)
		{
			
			PCOS_text=PCOS_text+"Недостаточно данных для диагностики СПКЯ. Требуется дообследование "

			if (ex_prl==null)
			{
				PCOS_text=PCOS_text+"(пролактин?); "
			}	
			if (ex_tsh==null)
			{
				PCOS_text=PCOS_text+"(ТТГ?); "
			}	
			if (ex_17ph==null)
			{
				PCOS_text=PCOS_text+"(17-OH прогестерон?); "
			}	
			if (ex_pnya==null)
			{
				PCOS_text=PCOS_text+"(отсутствуют данные о преждевременной недостаточности яичников); "
			}	
			
		}

		if (F_PCOS==null && ex==1)
		{
			if (ex_prl==1)
			{
				PCOS_text=PCOS_text+"Повышенный пролактин (гиперпролактинемия (Е22.1) ?) ("+value_prl_+"). "
			}	
			if (ex_tsh==1)
			{
				PCOS_text=PCOS_text+"Повышение ТТГ (тиреотоксикоз (гипертиреоз) Е05 ?)("+tsh+"). "
			}	
			if (ex_17ph==1)
			{
				PCOS_text=PCOS_text+"Повышение 17-OH прогестерона("+value_17hp_+"). "
			}	
			if (ex_pnya==1)
			{
				PCOS_text=PCOS_text+"Преждевременная недостаточность яичников."
			}	
		}

return [F_PCOS,ex,grey,F_Phenotype,PCOS_text]
}
