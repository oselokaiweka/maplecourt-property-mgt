# This script generates pdf of mc1 reports and the 
# main function is called in the mc1_nsc_monthly_report.py

import os
import datetime
from reportlab.lib import colors, pagesizes
from reportlab.lib.units import inch
from reportlab.platypus import Paragraph, Spacer
from reportlab.lib.pagesizes import LEGAL
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import PageTemplate, BaseDocTemplate, PageBreak, NextPageTemplate
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Image, Frame

def generate_pdf(nsc_table_data, nsc_subtotal, nsc_management_fee, nsc_grand_total, # <<< NSC VARIABLES
                mgtfee_table_data, total_mgt_fee, first_day_prev_month_str, # <<< MGT FEE VARIABLES
                sc_table_data, sc_summary_list, # <<< SC VARIABLES 
                inflow_records): # <<< INFLOW VARIABLES    
    
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
    dir_path = os.environ.get('DIR_PATH')
    logo = Image(dir_path+'/images/business_logo.png', width=2.1*inch, height=0.8*inch)
    logo.spaceAfter = 5
    logo.hAlign = 'LEFT'
    elements.append(logo)

    # Initializing date variable
    current_date = datetime.date.today()
    today = current_date.strftime("%d-%m-%Y")

    # Add document titles
    property_name = Paragraph(f"MAPLE COURT 1 - JABI", left_aligned_title)
    property_name.spaceAfter = 2
    elements.append(property_name)

    main_title = Paragraph(f"EXPENSES REPORT & MANAGEMENT INVOICE - 31 OCT 2023", left_aligned_title)
    main_title.spaceAfter = 10
    elements.append(main_title)

    bill_to = Paragraph(f"Bill to: MRS CAROLINE MORAH", left_aligned_normal_bold)
    bill_to.spaceAfter = 2
    elements.append(bill_to)

    invoice_id = Paragraph(f"Invoice id: PMG/MC1/F1-7/{today.month}/{today.year}", left_aligned_normal_bold)
    invoice_id.spaceAfter = 5
    elements.append(invoice_id)

    # Create a summary table for all sections
    summary_table_style = common_table_style + [
        ('BACKGROUND', (0,-1), (-1,-1), colors.lightgreen),
        ('ALIGN', (1,0), (1,-1), 'LEFT'),
        ('ALIGN', (-1,0), (-1,-1), 'RIGHT'),
        ('FONTNAME', (0,-1), (-1,-1), 'Helvetica-Bold')
    ]

    summary_table_data = [
        ['SUMMARY', 'REF CODE','AMOUNT(NGN)'],
        ['OCTOBER - NOVEMBER SERVICE CHARGE:', 'MC1L1 SC', '525,000.00'],
        ['NOVEMBER INCIDENTALS:', 'MC1L1 NSC', '25,000.00'], 
        ['SEPTEMBER - OCTOBER REIMBURSABLE:', 'MC1L1 NSC', f'{nsc_grand_total}'],
        ['SEPTEMBER - OCTOBER MANAGEMENT FEE:', 'MC1L1 MGT', f'{total_mgt_fee}' ],
        ['TOTAL:', '' ,'N 1,086,068.87']
    ]
    
    summary_table = Table(summary_table_data, colWidths=[355, 95, 95], hAlign='LEFT')
    summary_table.setStyle(TableStyle(summary_table_style))
    summary_table.spaceAfter = 15
    elements.append(summary_table)


    # Building service charge report section
    nsc_report_title = Paragraph(f"SERVICE CHARGE RECURRING EXPENSES - [ September {current_date.year} ]", left_aligned_normal_bold) 
    nsc_report_title.spaceAfter = 2
    elements.append(nsc_report_title)    

    sc_table = Table(sc_table_data, colWidths=[30, 35, 80, 305, 95], hAlign='LEFT')
    sc_table.setStyle(TableStyle(common_table_style))
    sc_table.spaceAfter = 0
    elements.append(sc_table)

    # Create a sum_table for sub-total, management_fee and grand_total for nsc table
    sc_sum_table_data = [
        ['SUB-TOTAL', f'{sc_summary_list[0]:,.2f}'],
        ['7.5% MANAGEMENT FEE', f'{sc_summary_list[1]:,.2f}'],
        ['GRAND TOTAL', f'{sc_summary_list[2]:,.2f}'],
        ['BALANCE BROUGHT FORWARD', inflow_records[0][1] - total_sc_expenses], #f'{all_total - MC1L1_SC_NSC_MGT_LIST[1]:,.2f}'
        ['TOTAL RECEIVED (Aug-Sept SC & N300k Diesel)', f'{825000:,.2f}'],
        ['NET TOTAL', f'{94569.38:,.2f}']
    ]

    sc_sum_table = Table(sc_sum_table_data, colWidths=[450, 95], hAlign='LEFT')
    sc_sum_table.setStyle(TableStyle(summary_table_style))
    sc_sum_table.spaceAfter = 15
    elements.append(sc_sum_table)

    # Building service charge 2 temp report section
    nsc_report_title = Paragraph(f"SERVICE CHARGE RECURRING EXPENSES - [ October {current_date.year}]", left_aligned_normal_bold) 
    nsc_report_title.spaceAfter = 2
    elements.append(nsc_report_title)    

    sc_table = Table(oct_sc_table_data, colWidths=[30, 35, 80, 305, 95], hAlign='LEFT')
    sc_table.setStyle(TableStyle(common_table_style))
    sc_table.spaceAfter = 0
    elements.append(sc_table)

    # Create a sum_table for sub-total, management_fee and grand_total for nsc table
    oct_sc_sum_table_data = [
        ['SUB-TOTAL', f'{oct_sc_summary_list[0]:,.2f}'],
        ['7.5% MANAGEMENT FEE', f'{oct_sc_summary_list[1]:,.2f}'],
        ['GRAND TOTAL', f'{oct_sc_summary_list[2]:,.2f}'],
        ['BALANCE BROUGHT FORWARD', f'{94569.38:,.2f}' ], #f'{all_total - MC1L1_SC_NSC_MGT_LIST[1]:,.2f}'
        ['TOTAL RECEIVED (N350k Diesel)', f'{350000:,.2f}'],
        ['NET TOTAL', f'{116213.98:,.2f}']
    ]

    sc_sum_table = Table(oct_sc_sum_table_data, colWidths=[450, 95], hAlign='LEFT')
    sc_sum_table.setStyle(TableStyle(summary_table_style))
    sc_sum_table.spaceAfter = 15
    elements.append(sc_sum_table)


    # Building non-service charge report section
    nsc_report_title = Paragraph(f"NON-SERVICE CHARGE REIMBURSABLE EXPENSES - [ {datetime.datetime.strptime((nsc_table_data[1][2]), '%Y-%m-%d').strftime('%d-%m-%Y')} to 31-10-2023 ]", left_aligned_normal_bold) 
    nsc_report_title.spaceAfter = 2
    elements.append(nsc_report_title)    

    nsc_table = Table(nsc_table_data, colWidths=[30, 35, 80, 305, 95], hAlign='LEFT')
    nsc_table.setStyle(TableStyle(common_table_style))
    nsc_table.spaceAfter = 0
    elements.append(nsc_table)

    # Create a sum_table for sub-total, management_fee and grand_total for nsc table
    sum_table_data = [
        ['SUB-TOTAL',nsc_subtotal],
        ['7.5% MANAGEMENT FEE', nsc_management_fee],
        ['GRAND TOTAL', nsc_grand_total]
    ]

    sum_table = Table(sum_table_data, colWidths=[450, 95], hAlign='LEFT')
    sum_table.setStyle(TableStyle(summary_table_style))
    sum_table.spaceAfter = 15
    elements.append(sum_table)


    # Building management fee report section
    mgt_report_title = Paragraph(f"MANAGEMENT FEE [ {first_day_prev_month_str.strftime('%B')} to October {current_date.year} ]", left_aligned_normal_bold)
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
    total_mgt_fee_data = [['TOTAL MANAGEMENT FEE FOR PERIOD', total_mgt_fee]]
    total_mgt_fee_table = Table(total_mgt_fee_data, colWidths=[465, 80], hAlign='LEFT')
    total_mgt_fee_table.setStyle(TableStyle(summary_table_style))
    total_mgt_fee_table.spaceAfter = 20
    elements.append(total_mgt_fee_table)


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
