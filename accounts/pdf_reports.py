"""
PDF Report Generator for Patient Treatment Progress
"""

import os
import io
from datetime import datetime
from django.conf import settings
from django.http import HttpResponse
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from PIL import Image as PILImage
import requests

class PatientReportGenerator:
    """Generate comprehensive PDF reports for patient treatment progress"""
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self.setup_custom_styles()
    
    def setup_custom_styles(self):
        """Define custom styles for the report"""
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=18,
            spaceAfter=30,
            textColor=colors.HexColor('#2c5f8b'),
            alignment=1  # Center alignment
        ))
        
        self.styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=self.styles['Heading2'],
            fontSize=14,
            spaceBefore=20,
            spaceAfter=10,
            textColor=colors.HexColor('#1f4e79'),
            borderWidth=1,
            borderColor=colors.HexColor('#1f4e79'),
            borderPadding=5,
            backColor=colors.HexColor('#f0f8ff')
        ))
        
        self.styles.add(ParagraphStyle(
            name='StepTitle',
            parent=self.styles['Heading3'],
            fontSize=12,
            spaceBefore=15,
            spaceAfter=8,
            textColor=colors.HexColor('#333333'),
            fontName='Helvetica-Bold'
        ))
    
    def generate_patient_report(self, patient, doctor=None):
        """Generate a comprehensive PDF report for a patient"""
        buffer = io.BytesIO()
        
        # Create the PDF object
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=18
        )
        
        # Container for the 'Flowable' objects
        story = []
        
        # Add header
        self._add_header(story, patient, doctor)
        
        # Add patient information
        self._add_patient_info(story, patient)
        
        # Add treatment overview
        self._add_treatment_overview(story, patient)
        
        # Add treatment steps details
        self._add_treatment_steps(story, patient)
        
        # Add progress summary
        self._add_progress_summary(story, patient)
        
        # Add footer
        self._add_footer(story)
        
        # Build PDF
        doc.build(story)
        
        # Get the value of the BytesIO buffer and return it
        pdf = buffer.getvalue()
        buffer.close()
        
        return pdf
    
    def _add_header(self, story, patient, doctor):
        """Add report header with clinic/doctor info"""
        # Title
        title = Paragraph(
            f"PATIENT TREATMENT REPORT",
            self.styles['CustomTitle']
        )
        story.append(title)
        
        # Report info table
        report_data = [
            ['Report Generated:', datetime.now().strftime('%B %d, %Y at %I:%M %p')],
            ['Patient:', f"{patient.user.get_full_name() or patient.user.username}"],
            ['Patient Email:', patient.user.email],
            ['Doctor:', f"Dr. {doctor.user.get_full_name()}" if doctor else "Not Assigned"],
            ['Report ID:', f"RPT-{patient.id}-{datetime.now().strftime('%Y%m%d')}"]
        ]
        
        report_table = Table(report_data, colWidths=[2*inch, 4*inch])
        report_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#e8f4f8')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#cccccc')),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        
        story.append(report_table)
        story.append(Spacer(1, 20))
    
    def _add_patient_info(self, story, patient):
        """Add patient basic information section"""
        section_title = Paragraph("PATIENT INFORMATION", self.styles['SectionHeader'])
        story.append(section_title)
        
        # Patient details
        patient_data = [
            ['Full Name:', patient.user.get_full_name() or patient.user.username],
            ['Email:', patient.user.email],
            ['Phone:', patient.phone or 'Not provided'],
            ['Registration Date:', patient.user.date_joined.strftime('%B %d, %Y')],
            ['Account Status:', 'Active' if patient.user.is_active else 'Inactive']
        ]
        
        patient_table = Table(patient_data, colWidths=[2*inch, 4*inch])
        patient_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f9f9f9')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#dddddd')),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        
        story.append(patient_table)
        story.append(Spacer(1, 20))
    
    def _add_treatment_overview(self, story, patient):
        """Add treatment overview section"""
        section_title = Paragraph("TREATMENT OVERVIEW", self.styles['SectionHeader'])
        story.append(section_title)
        
        try:
            treatment = patient.patient_treatment
            steps = treatment.steps.all().order_by('order')
            
            # Treatment summary
            total_steps = steps.count()
            completed_steps = steps.filter(is_completed=True).count()
            active_step = steps.filter(is_active=True).first()
            
            overview_data = [
                ['Total Steps:', str(total_steps)],
                ['Completed Steps:', f"{completed_steps} of {total_steps}"],
                ['Progress:', f"{(completed_steps/total_steps*100):.1f}%" if total_steps > 0 else "0%"],
                ['Current Step:', active_step.name if active_step else "No active step"],
                ['Treatment Status:', "In Progress" if active_step else ("Completed" if completed_steps == total_steps else "Not Started")]
            ]
            
            overview_table = Table(overview_data, colWidths=[2*inch, 4*inch])
            overview_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#e8f5e8')),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#cccccc')),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ]))
            
            story.append(overview_table)
            
        except Exception as e:
            error_text = Paragraph(
                f"No treatment data available for this patient.",
                self.styles['Normal']
            )
            story.append(error_text)
        
        story.append(Spacer(1, 20))
    
    def _add_treatment_steps(self, story, patient):
        """Add detailed treatment steps section"""
        section_title = Paragraph("TREATMENT STEPS DETAILS", self.styles['SectionHeader'])
        story.append(section_title)
        
        try:
            treatment = patient.patient_treatment
            steps = treatment.steps.all().order_by('order')
            
            if not steps.exists():
                no_steps_text = Paragraph(
                    "No treatment steps have been created for this patient yet.",
                    self.styles['Normal']
                )
                story.append(no_steps_text)
                return
            
            for step in steps:
                # Step header
                status_icon = "✅" if step.is_completed else ("🟢" if step.is_active else "⭕")
                step_title = f"{status_icon} Step {step.order}: {step.name}"
                
                step_header = Paragraph(step_title, self.styles['StepTitle'])
                story.append(step_header)
                
                # Step details table
                step_data = [
                    ['Description:', step.description or 'No description provided'],
                    ['Duration:', f"{step.duration_days} days"],
                    ['Start Date:', step.start_date.strftime('%B %d, %Y')],
                    ['Status:', "Completed" if step.is_completed else ("Active" if step.is_active else "Pending")],
                    ['Photos Uploaded:', str(step.photos.count())],
                ]
                
                if step.is_completed and step.notification_sent:
                    step_data.append(['Completion Email:', 'Sent'])
                
                step_table = Table(step_data, colWidths=[1.5*inch, 4.5*inch])
                step_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f0f0f0')),
                    ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, -1), 9),
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cccccc')),
                    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ]))
                
                story.append(step_table)
                
                # Add photos if available
                photos = step.photos.all()[:4]  # Limit to first 4 photos
                if photos.exists():
                    photos_text = Paragraph(
                        f"<b>Progress Photos ({photos.count()} uploaded):</b>",
                        self.styles['Normal']
                    )
                    story.append(Spacer(1, 5))
                    story.append(photos_text)
                    
                    # Create photo grid (2x2)
                    photo_data = []
                    photo_row = []
                    
                    for i, photo in enumerate(photos):
                        try:
                            # Create small thumbnail representation
                            photo_info = f"Photo {i+1}\n{photo.uploaded_at.strftime('%m/%d/%Y')}"
                            photo_row.append(photo_info)
                            
                            if len(photo_row) == 2 or i == len(photos) - 1:
                                photo_data.append(photo_row)
                                photo_row = []
                        except Exception:
                            continue
                    
                    if photo_data:
                        photo_table = Table(photo_data, colWidths=[3*inch, 3*inch])
                        photo_table.setStyle(TableStyle([
                            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f8f8f8')),
                            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                            ('FONTSIZE', (0, 0), (-1, -1), 8),
                            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#dddddd')),
                            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                        ]))
                        story.append(photo_table)
                
                story.append(Spacer(1, 15))
                
        except Exception as e:
            error_text = Paragraph(
                f"Error loading treatment steps: {str(e)}",
                self.styles['Normal']
            )
            story.append(error_text)
    
    def _add_progress_summary(self, story, patient):
        """Add progress summary and recommendations"""
        section_title = Paragraph("PROGRESS SUMMARY & RECOMMENDATIONS", self.styles['SectionHeader'])
        story.append(section_title)
        
        try:
            treatment = patient.patient_treatment
            steps = treatment.steps.all().order_by('order')
            
            total_steps = steps.count()
            completed_steps = steps.filter(is_completed=True).count()
            total_photos = sum(step.photos.count() for step in steps)
            
            # Progress analysis
            if total_steps == 0:
                summary_text = "No treatment plan has been established for this patient yet."
            elif completed_steps == 0:
                summary_text = "Patient has not started treatment yet. Consider scheduling an initial consultation."
            elif completed_steps == total_steps:
                summary_text = "🎉 Congratulations! Patient has successfully completed all treatment steps."
            else:
                progress_percent = (completed_steps / total_steps) * 100
                summary_text = f"Patient is {progress_percent:.1f}% through their treatment plan ({completed_steps}/{total_steps} steps completed)."
            
            summary_para = Paragraph(summary_text, self.styles['Normal'])
            story.append(summary_para)
            story.append(Spacer(1, 10))
            
            # Recommendations
            recommendations = []
            
            if total_steps == 0:
                recommendations.append("• Create initial treatment plan with appropriate steps")
                recommendations.append("• Schedule patient consultation to discuss treatment goals")
            
            elif completed_steps < total_steps:
                active_step = steps.filter(is_active=True).first()
                if active_step:
                    recommendations.append(f"• Monitor progress of current step: '{active_step.name}'")
                    recommendations.append("• Encourage patient to upload progress photos regularly")
                else:
                    recommendations.append("• Activate the next treatment step for the patient")
            
            if total_photos == 0:
                recommendations.append("• Encourage patient to upload progress photos for better tracking")
            
            recommendations.append("• Schedule regular follow-up appointments")
            recommendations.append("• Monitor patient compliance with treatment plan")
            
            if recommendations:
                rec_title = Paragraph("<b>Recommendations:</b>", self.styles['Normal'])
                story.append(rec_title)
                
                for rec in recommendations:
                    rec_para = Paragraph(rec, self.styles['Normal'])
                    story.append(rec_para)
            
        except Exception as e:
            error_text = Paragraph(
                f"Unable to generate progress summary.",
                self.styles['Normal']
            )
            story.append(error_text)
        
        story.append(Spacer(1, 20))
    
    def _add_footer(self, story):
        """Add report footer"""
        footer_text = Paragraph(
            f"<i>This report was generated automatically on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}. "
            f"For questions about this report, please contact your medical provider.</i>",
            self.styles['Normal']
        )
        story.append(Spacer(1, 20))
        story.append(footer_text)


def generate_patient_pdf_report(patient_id, doctor_id=None):
    """
    Generate PDF report for a specific patient
    """
    from .models import Patient, Doctor
    
    try:
        patient = Patient.objects.select_related('user', 'doctor').get(id=patient_id)
        doctor = None
        
        if doctor_id:
            doctor = Doctor.objects.select_related('user').get(id=doctor_id)
        elif patient.doctor:
            doctor = patient.doctor
        
        generator = PatientReportGenerator()
        pdf_content = generator.generate_patient_report(patient, doctor)
        
        return pdf_content
        
    except Patient.DoesNotExist:
        raise ValueError(f"Patient with ID {patient_id} not found")
    except Doctor.DoesNotExist:
        raise ValueError(f"Doctor with ID {doctor_id} not found")
    except Exception as e:
        raise ValueError(f"Error generating report: {str(e)}")
