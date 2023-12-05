# This script generates pdf of mc1 reports and the 
# main function is called in the mc1_nsc_monthly_report.py

import os, json
from datetime import datetime
from reportlab.lib import colors, pagesizes
from reportlab.lib.units import inch
from reportlab.platypus import Paragraph, Spacer
from reportlab.lib.pagesizes import LEGAL
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import PageTemplate, BaseDocTemplate, PageBreak, NextPageTemplate
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Image, Frame
dir_path = os.environ.get('DIR_PATH')

def generate_pdf(nsc_table_data, nsc_summary_dict, # <<< NSC VARIABLES
                mgtfee_table_data, mgtfee_summary_dict, # <<< MGT FEE VARIABLES
                sc_table_data, sc_summary_dict, # <<< SC VARIABLES 
                inflow_records, period_start): # <<< INFLOW VARIABLES, START DATE   
    
    pdf = SimpleDocTemplate('MC1_REPORT.PDF', pagesize=LEGAL) # Creates a PDF document
    elements = [] # Creates a list to store the content

    # Define PageTemplate for the first page 
    first_page_template = PageTemplate(id='FirstPage', frames=Frame(
        0, 0, pagesizes.LEGAL[0], pagesizes.LEGAL[1], leftPadding=33, rightPadding=30, topPadding=20, bottomPadding=20)
    )

    # Define PageTemplate for the subsequent pages
    subsequent_page_template = PageTemplate(id='SubsequentPages', frames=Frame(
        0, 0, pagesizes.LEGAL[0], pagesizes.LEGAL[1], leftPadding=33, rightPadding=30, topPadding=20, bottomPadding=20)
    )
    
    # Register the page templates
    pdf.addPageTemplates([first_page_template, subsequent_page_template])
    elements.append(NextPageTemplate('SubsequentPages'))

    # Creating styles for formating and aligning texts
    left_aligned_title = getSampleStyleSheet()['Title']
    left_aligned_title.alignment = 0 #0 means left alignment
    
    left_aligned_normal = getSampleStyleSheet()['Normal']
    left_aligned_normal.alignment = 0

    left_aligned_normal_bold = ParagraphStyle('BoldTitle', parent=left_aligned_normal)
    left_aligned_normal_bold.fontName = 'Helvetica-Bold'
    left_aligned_normal_bold.alignment = 0

    # Creating common table style 
    common_table_style = [
        ('BACKGROUND', (0,0), (-1,0), colors.lightgreen),
        ('TEXTCOLOR', (0,0), (-1,0), colors.black),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'), # Aligns column 1 to 5 (S/N) to the left
        ('ALIGN', (1,0), (1,-1), 'CENTER'), # Aligns column 2 of 5 (ID) to the center
        ('ALIGN', (-1,0), (-1,-1), 'RIGHT'), # Align column 5 of 5 (Amount) to the right
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0,1), (-1,0), 12),
        ('BACKGROUND', (0,1), (-1,-1), colors.white),
        ('GRID', (0,0), (-1,-1), 1, colors.darkgrey)
    ]

    # Add business logo
    logo = Image(dir_path+'/images/business_logo.png', width=2.1*inch, height=0.8*inch)
    logo.spaceAfter = 5
    logo.hAlign = 'LEFT'
    elements.append(logo)

    # Initializing date variable
    curr_date = datetime.now()
    report_start = datetime.strptime(period_start,'%Y-%m-%d') if period_start is not None else curr_date.replace(day=1)

    # Add document titles
    property_name = Paragraph(f"MAPLE COURT 1 - JABI", left_aligned_title)
    property_name.spaceAfter = 2
    elements.append(property_name)

    main_title = Paragraph(f"EXPENSES REPORT & MANAGEMENT INVOICE - {report_start.strftime('%b %Y')}", left_aligned_title)
    main_title.spaceAfter = 10
    elements.append(main_title)

    bill_to = Paragraph(f"Bill to: MRS CAROLINE MORAH", left_aligned_normal_bold)
    bill_to.spaceAfter = 2
    elements.append(bill_to)

    invoice_id = Paragraph(f"Invoice id: PMG/MC1/F1-7/{report_start.strftime('%m')}/{report_start.strftime('%y')}", left_aligned_normal_bold)
    invoice_id.spaceAfter = 5
    elements.append(invoice_id)

    # Retrieve relevant fixed values from mc_app_data.json file
    try:
        with open(dir_path+"/mc_app_data.json", "r") as app_data_file: # Get app data from json file
            app_data = json.load(app_data_file)
        bills_data = app_data['bills']
        service_charge = float(app_data['rates']['service_charge'])
        incidentals =  float(app_data['rates']['incidentals'])
    except Exception as e:
        print('Unable to retrieve app data')

    # Create a summary table for all sections
    summary_table_style = common_table_style + [
        ('BACKGROUND', (0,-1), (-1,-1), colors.lightgreen),
        ('ALIGN', (1,0), (1,-1), 'LEFT'),
        ('ALIGN', (-1,0), (-1,-1), 'RIGHT'),
        ('FONTNAME', (0,-1), (-1,-1), 'Helvetica-Bold')
    ]

    summary_table_data = [
        ['SUMMARY', 'REF CODE','AMOUNT(NGN)'],
        [f"{report_start.replace(month=(report_start.month + 1) % 12 if report_start.month != 11 else 12).strftime('%B').upper()} SERVICE CHARGE:", 'MC1L1 SC', f'{service_charge:,.2f}'],
        [f"{report_start.replace(month=(report_start.month + 1) % 12 if report_start.month != 11 else 12).strftime('%B').upper()} INCIDENTALS:", 'MC1L1 NSC', f'{incidentals:,.2f}'], 
        [f"{report_start.strftime('%B').upper()} REIMBURSABLE:", 'MC1L1 NSC', f"{nsc_summary_dict['grand_total']:,.2f}"],
        [f"{report_start.strftime('%B').upper()} MANAGEMENT FEE:", 'MC1L1 MGT', f"{mgtfee_summary_dict['total_mgt_fee']:,.2f}"],
        ['TOTAL:', '' ,f"N{service_charge + incidentals + nsc_summary_dict['grand_total'] + mgtfee_summary_dict['total_mgt_fee']:,.2f}"]
    ]
    
    summary_table = Table(summary_table_data, colWidths=[355, 95, 95], hAlign='LEFT')
    summary_table.setStyle(TableStyle(summary_table_style))
    summary_table.spaceAfter = 15
    elements.append(summary_table)


    # Building management fee report section
    mgt_report_title = Paragraph(f"MANAGEMENT FEE [ {mgtfee_summary_dict['period_start'].strftime('%B %Y')} ]", left_aligned_normal_bold)
    mgt_report_title.spaceAfter = 2
    elements.append(mgt_report_title)

    # Creating mgt fee table style
    mgtfee_table_style = common_table_style + [
        ('ALIGN', (0,0), (3,-1), 'CENTER'), 
        ('ALIGN', (1,0), (1,-1), 'LEFT'), 
        ('ALIGN', (4,0), (7,-1), 'RIGHT'), 
        ('ALIGN', (6,0), (6,-1), 'CENTER') 
    ]

    # Create mgt fee table to display data
    mgtfee_table = Table(mgtfee_table_data, colWidths=[45, 115, 75, 75, 65, 55, 35, 80], hAlign='LEFT')
    mgtfee_table.setStyle(TableStyle(mgtfee_table_style))
    mgtfee_table.spaceAfter = 0
    elements.append(mgtfee_table)

    # Create table to display total mgt fee
    total_mgt_fee_data = [
        ['TOTAL MANAGEMENT FEE FOR PERIOD', f"{mgtfee_summary_dict['total_mgt_fee']:,.2f}"],
        ['OUTSTANDING MANAGEMENT FEE', f"{bills_data['mgt']['bill_outstanding']:,.2f}"],
        ['NET PAYABLE MANAGEMENT FEE', f"{mgtfee_summary_dict['total_mgt_fee'] + bills_data['mgt']['bill_outstanding']:,.2f}" ]
    ]
    total_mgt_fee_table = Table(total_mgt_fee_data, colWidths=[465, 80], hAlign='LEFT')
    total_mgt_fee_table.setStyle(TableStyle(summary_table_style))
    total_mgt_fee_table.spaceAfter = 15
    elements.append(total_mgt_fee_table)


    # Building non-service charge report section
    nsc_report_title = Paragraph(f"NON-SERVICE CHARGE REIMBURSABLE EXPENSES - [ {datetime.strptime((nsc_table_data[1][2]), '%Y-%m-%d').strftime('%d-%m-%Y')} to {datetime.now().strftime('%d-%m-%Y')} ]", left_aligned_normal_bold) 
    nsc_report_title.spaceAfter = 2
    elements.append(nsc_report_title)    

    nsc_table = Table(nsc_table_data, colWidths=[30, 35, 80, 305, 95], hAlign='LEFT')
    nsc_table.setStyle(TableStyle(common_table_style))
    nsc_table.spaceAfter = 0
    elements.append(nsc_table)

    # Create a sum_table for sub-total, management_fee and grand_total for nsc table
    sum_table_data = [
        ['SUB-TOTAL',f"{nsc_summary_dict['subtotal']:,.2f}"],
        ['7.5% MANAGEMENT FEE', f"{nsc_summary_dict['mgt_fee']:,.2f}"],
        ['TOTAL REIMBURSABLE EXPENSES FOR PERIOD', f"{nsc_summary_dict['grand_total']:,.2f}"],
        ['PREVIOUS BALANCE BROUGHT FORWARD', f"{bills_data['nsc']['bill_outstanding']:,.2f}"],
        ['NET PAYABLE REIMBURSABLE EXPENSES', F"{nsc_summary_dict['grand_total'] + bills_data['nsc']['bill_outstanding']:,.2f}"]
    ]

    sum_table = Table(sum_table_data, colWidths=[450, 95], hAlign='LEFT')
    sum_table.setStyle(TableStyle(summary_table_style))
    sum_table.spaceAfter = 15
    elements.append(sum_table)

    # Building service charge report section
    nsc_report_title = Paragraph(f"SERVICE CHARGE RECURRING EXPENSES - [ {report_start.strftime('%B %Y')} ]", left_aligned_normal_bold) 
    nsc_report_title.spaceAfter = 2
    elements.append(nsc_report_title)    

    sc_table = Table(sc_table_data, colWidths=[30, 35, 80, 305, 95], hAlign='LEFT')
    sc_table.setStyle(TableStyle(common_table_style))
    sc_table.spaceAfter = 0
    elements.append(sc_table)

    # Create a sum_table for sub-total, management_fee and grand_total for nsc table
    sc_sum_table_data = [
        ['SUB-TOTAL', f"{sc_summary_dict['subtotal']:,.2f}"],
        ['7.5% MANAGEMENT FEE', f"{sc_summary_dict['mgt_fee']:,.2f}"],
        ['TOTAL SERVICE CHARGE EXPENSES FOR PERIOD', f"{sc_summary_dict['grand_total']:,.2f}"],
        ['BALANCE BROUGHT FORWARD', f"{bills_data['sc']['bill_outstanding']:,.2f}"], #f'{all_total - MC1L1_SC_NSC_MGT_LIST[1]:,.2f}'
        ['TOTAL RECEIVED (Aug-Sept SC & N300k Diesel)', f"{bills_data['sc']['received'] + app_data['payments']['diesel_contribution']:,.2f}"],
        ['NET TOTAL', f'{94569.38:,.2f}']
    ]

    sc_sum_table = Table(sc_sum_table_data, colWidths=[450, 95], hAlign='LEFT')
    sc_sum_table.setStyle(TableStyle(summary_table_style))
    sc_sum_table.spaceAfter = 20
    elements.append(sc_sum_table)


    # Add closing remarks / name / designation
    closing_remark1 = Paragraph(f"Kindly make payments in favour of CHROMETRO NIG LTD, GTBank: 0117443245.", left_aligned_normal_bold) 
    closing_remark2 = Paragraph(f"Thank you for your business, it is greatly appreciated.", left_aligned_normal_bold) 
    closing_remark2.spaceAfter = 15
    closing_remark3 = Paragraph(f"Yours faithfully,", left_aligned_normal_bold) 
    closing_remark3.spaceAfter = 5

    elements.append(closing_remark1) 
    elements.append(closing_remark2) 
    elements.append(closing_remark3) 

    # Add signature
    signature = Image(dir_path+'/images/signature.png', width=2.46*inch, height=0.984*inch)
    signature.spaceAfter = 2
    signature.hAlign = 'LEFT'
    elements.append(signature)

    name = Paragraph(f"OSELOKA IWEKA CHINEDU", left_aligned_normal_bold) 
    designation = Paragraph(f"MANAGING DIRECTOR", left_aligned_normal_bold) 
    elements.append(name) 
    elements.append(designation) 

    pdf.build(elements)
