SELECT * FROM all_patients_data
inner join inpatient_data
ON all_patients_data.Patient_ID = inpatient_data.Patient_ID 
inner join lab_data
ON all_patients_data.Patient_ID = lab_data.Patient_ID
inner join pharmacy_data
ON all_patients_data.Patient_ID = pharmacy_data.Patient_ID;
