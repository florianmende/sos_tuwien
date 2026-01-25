"""
German Credit Dataset Description in RDF Triples
Using PROV-O, Croissant, and Schema.org vocabularies
"""

data_description_triples = [
    # Dataset Entity (Core Information)
    ':raw_data rdf:type prov:Entity .',
    ':raw_data rdf:type sc:Dataset .',
    ':raw_data rdf:type cr:Dataset .',
    ':raw_data sc:name "credit-g" .',
    ':raw_data sc:version "1" .',
    ':raw_data sc:inLanguage "en" .',
    ':raw_data sc:license "Public" .',
    ':raw_data sc:isAccessibleForFree true .',
    ':raw_data sc:url <https://www.openml.org/d/31> .',
    ':raw_data sc:sameAs <https://archive.ics.uci.edu/ml/datasets/statlog+(german+credit+data)> .',
    ':raw_data <http://purl.org/dc/terms/conformsTo> <http://mlcommons.org/croissant/1.0> .',
    ':raw_data cr:citeAs <https://dl.acm.org/doi/abs/10.1145/967900.968104> .',
    ':raw_data sc:description "Classification dataset for credit risk assessment. Classifies people described by a set of attributes as good or bad credit risks. Contains 20 features including checking account status, credit history, loan purpose, credit amount, savings, employment, personal status, age, and other financial indicators." .',
    ':raw_data sc:dateCreated "2014-04-06T23:21:47"^^xsd:dateTime .',
    ':raw_data sc:datePublished "1994-11-17T00:00:00"^^xsd:dateTime .',
    
    # Provenance - Attribution
    ':raw_data prov:wasAttributedTo :dr-hans-hofmann .',
    ':raw_data prov:wasGeneratedBy :dataset-creation-activity .',
    ':raw_data prov:wasDerivedFrom :uci-ml-repository .',
    ':raw_data prov:generatedAtTime "1994-11-17T00:00:00"^^xsd:dateTime .',
    ':raw_data prov:hadPrimarySource :uci-ml-repository .',
    
    # Creator Agent
    ':dr-hans-hofmann rdf:type prov:Agent .',
    ':dr-hans-hofmann rdf:type foaf:Person .',
    ':dr-hans-hofmann rdf:type sc:Person .',
    ':dr-hans-hofmann foaf:name "Dr. Hans Hofmann" .',
    ':dr-hans-hofmann sc:name "Dr. Hans Hofmann" .',
    
    # Source Repository
    ':uci-ml-repository rdf:type prov:Entity .',
    ':uci-ml-repository rdf:type sc:DataCatalog .',
    ':uci-ml-repository sc:name "UCI Machine Learning Repository" .',
    ':uci-ml-repository sc:url <https://archive.ics.uci.edu/ml/datasets/statlog+(german+credit+data)> .',
    ':uci-ml-repository <http://purl.org/dc/terms/description> "Source repository containing the original German Credit dataset" .',
    
    # Dataset Creation Activity
    ':dataset-creation-activity rdf:type prov:Activity .',
    ':dataset-creation-activity prov:startedAtTime "1994-11-17T00:00:00"^^xsd:dateTime .',
    ':dataset-creation-activity prov:endedAtTime "1994-11-17T00:00:00"^^xsd:dateTime .',
    ':dataset-creation-activity prov:wasAssociatedWith :dr-hans-hofmann .',
    ':dataset-creation-activity prov:used :uci-ml-repository .',
    ':dataset-creation-activity <http://purl.org/dc/terms/description> "Original creation and collection of German credit risk data" .',
    
    # Distribution - ARFF File (Local)
    ':credit-g-arff rdf:type cr:FileObject .',
    ':credit-g-arff rdf:type prov:Entity .',
    ':credit-g-arff rdf:type sc:DataDownload .',
    ':credit-g-arff sc:name "credit-g.arff" .',
    ':credit-g-arff sc:description "Local ARFF format distribution of the German Credit dataset" .',
    ':credit-g-arff sc:encodingFormat "text/arff" .',
    ':credit-g-arff cr:format "ARFF" .',
    ':credit-g-arff prov:wasDerivedFrom :raw_data .',
    ':raw_data sc:distribution :credit-g-arff .',
    
    # Record Set
    ':raw_recordset rdf:type cr:RecordSet .',
    ':raw_recordset sc:name "data-file-description" .',
    ':raw_recordset sc:description "Listing the fields of the data with 20 features and 1 target class" .',
    ':raw_recordset cr:source :credit-g-arff .',
    ':raw_data cr:recordSet :raw_recordset .',
    
    # Fields - All 20 features + 1 target
    ':raw_recordset cr:field :field-checking_status .',
    ':raw_recordset cr:field :field-duration .',
    ':raw_recordset cr:field :field-credit_history .',
    ':raw_recordset cr:field :field-purpose .',
    ':raw_recordset cr:field :field-credit_amount .',
    ':raw_recordset cr:field :field-savings_status .',
    ':raw_recordset cr:field :field-employment .',
    ':raw_recordset cr:field :field-installment_commitment .',
    ':raw_recordset cr:field :field-personal_status .',
    ':raw_recordset cr:field :field-other_parties .',
    ':raw_recordset cr:field :field-residence_since .',
    ':raw_recordset cr:field :field-property_magnitude .',
    ':raw_recordset cr:field :field-age .',
    ':raw_recordset cr:field :field-other_payment_plans .',
    ':raw_recordset cr:field :field-housing .',
    ':raw_recordset cr:field :field-existing_credits .',
    ':raw_recordset cr:field :field-job .',
    ':raw_recordset cr:field :field-num_dependents .',
    ':raw_recordset cr:field :field-own_telephone .',
    ':raw_recordset cr:field :field-foreign_worker .',
    ':raw_recordset cr:field :field-class .',
    
    # Field 0: checking_status
    ':field-checking_status rdf:type cr:Field .',
    ':field-checking_status sc:name "checking_status" .',
    ':field-checking_status sc:description "Status of existing checking account, in Deutsche Mark" .',
    ':field-checking_status cr:dataType sc:Text .',
    ':field-checking_status cr:source :credit-g-arff .',
    
    # Field 1: duration
    ':field-duration rdf:type cr:Field .',
    ':field-duration sc:name "duration" .',
    ':field-duration sc:description "Duration in months" .',
    ':field-duration cr:dataType sc:Integer .',
    ':field-duration cr:source :credit-g-arff .',
    
    # Field 2: credit_history
    ':field-credit_history rdf:type cr:Field .',
    ':field-credit_history sc:name "credit_history" .',
    ':field-credit_history sc:description "Credit history (credits taken, paid back duly, delays, critical accounts)" .',
    ':field-credit_history cr:dataType sc:Text .',
    ':field-credit_history cr:source :credit-g-arff .',
    
    # Field 3: purpose
    ':field-purpose rdf:type cr:Field .',
    ':field-purpose sc:name "purpose" .',
    ':field-purpose sc:description "Purpose of the credit (car, television, education, etc.)" .',
    ':field-purpose cr:dataType sc:Text .',
    ':field-purpose cr:source :credit-g-arff .',
    
    # Field 4: credit_amount
    ':field-credit_amount rdf:type cr:Field .',
    ':field-credit_amount sc:name "credit_amount" .',
    ':field-credit_amount sc:description "Credit amount in Deutsche Mark" .',
    ':field-credit_amount cr:dataType sc:Integer .',
    ':field-credit_amount cr:source :credit-g-arff .',
    
    # Field 5: savings_status
    ':field-savings_status rdf:type cr:Field .',
    ':field-savings_status sc:name "savings_status" .',
    ':field-savings_status sc:description "Status of savings account/bonds, in Deutsche Mark" .',
    ':field-savings_status cr:dataType sc:Text .',
    ':field-savings_status cr:source :credit-g-arff .',
    
    # Field 6: employment
    ':field-employment rdf:type cr:Field .',
    ':field-employment sc:name "employment" .',
    ':field-employment sc:description "Present employment, in number of years" .',
    ':field-employment cr:dataType sc:Text .',
    ':field-employment cr:source :credit-g-arff .',
    
    # Field 7: installment_commitment
    ':field-installment_commitment rdf:type cr:Field .',
    ':field-installment_commitment sc:name "installment_commitment" .',
    ':field-installment_commitment sc:description "Installment rate in percentage of disposable income" .',
    ':field-installment_commitment cr:dataType sc:Integer .',
    ':field-installment_commitment cr:source :credit-g-arff .',
    
    # Field 8: personal_status
    ':field-personal_status rdf:type cr:Field .',
    ':field-personal_status sc:name "personal_status" .',
    ':field-personal_status sc:description "Personal status (married, single, etc.) and sex" .',
    ':field-personal_status cr:dataType sc:Text .',
    ':field-personal_status cr:source :credit-g-arff .',
    
    # Field 9: other_parties
    ':field-other_parties rdf:type cr:Field .',
    ':field-other_parties sc:name "other_parties" .',
    ':field-other_parties sc:description "Other debtors / guarantors" .',
    ':field-other_parties cr:dataType sc:Text .',
    ':field-other_parties cr:source :credit-g-arff .',
    
    # Field 10: residence_since
    ':field-residence_since rdf:type cr:Field .',
    ':field-residence_since sc:name "residence_since" .',
    ':field-residence_since sc:description "Present residence since X years" .',
    ':field-residence_since cr:dataType sc:Integer .',
    ':field-residence_since cr:source :credit-g-arff .',
    
    # Field 11: property_magnitude
    ':field-property_magnitude rdf:type cr:Field .',
    ':field-property_magnitude sc:name "property_magnitude" .',
    ':field-property_magnitude sc:description "Property (e.g. real estate, car, life insurance)" .',
    ':field-property_magnitude cr:dataType sc:Text .',
    ':field-property_magnitude cr:source :credit-g-arff .',
    
    # Field 12: age
    ':field-age rdf:type cr:Field .',
    ':field-age sc:name "age" .',
    ':field-age sc:description "Age in years" .',
    ':field-age cr:dataType sc:Integer .',
    ':field-age cr:source :credit-g-arff .',
    
    # Field 13: other_payment_plans
    ':field-other_payment_plans rdf:type cr:Field .',
    ':field-other_payment_plans sc:name "other_payment_plans" .',
    ':field-other_payment_plans sc:description "Other installment plans (banks, stores)" .',
    ':field-other_payment_plans cr:dataType sc:Text .',
    ':field-other_payment_plans cr:source :credit-g-arff .',
    
    # Field 14: housing
    ':field-housing rdf:type cr:Field .',
    ':field-housing sc:name "housing" .',
    ':field-housing sc:description "Housing (rent, own, for free)" .',
    ':field-housing cr:dataType sc:Text .',
    ':field-housing cr:source :credit-g-arff .',
    
    # Field 15: existing_credits
    ':field-existing_credits rdf:type cr:Field .',
    ':field-existing_credits sc:name "existing_credits" .',
    ':field-existing_credits sc:description "Number of existing credits at this bank" .',
    ':field-existing_credits cr:dataType sc:Integer .',
    ':field-existing_credits cr:source :credit-g-arff .',
    
    # Field 16: job
    ':field-job rdf:type cr:Field .',
    ':field-job sc:name "job" .',
    ':field-job sc:description "Job status and qualification level" .',
    ':field-job cr:dataType sc:Text .',
    ':field-job cr:source :credit-g-arff .',
    
    # Field 17: num_dependents
    ':field-num_dependents rdf:type cr:Field .',
    ':field-num_dependents sc:name "num_dependents" .',
    ':field-num_dependents sc:description "Number of people being liable to provide maintenance for" .',
    ':field-num_dependents cr:dataType sc:Integer .',
    ':field-num_dependents cr:source :credit-g-arff .',
    
    # Field 18: own_telephone
    ':field-own_telephone rdf:type cr:Field .',
    ':field-own_telephone sc:name "own_telephone" .',
    ':field-own_telephone sc:description "Telephone (yes, no)" .',
    ':field-own_telephone cr:dataType sc:Text .',
    ':field-own_telephone cr:source :credit-g-arff .',
    
    # Field 19: foreign_worker
    ':field-foreign_worker rdf:type cr:Field .',
    ':field-foreign_worker sc:name "foreign_worker" .',
    ':field-foreign_worker sc:description "Foreign worker (yes, no)" .',
    ':field-foreign_worker cr:dataType sc:Text .',
    ':field-foreign_worker cr:source :credit-g-arff .',
    
    # Field 20: class (target variable)
    ':field-class rdf:type cr:Field .',
    ':field-class sc:name "class" .',
    ':field-class sc:description "Target classification: good or bad credit risk" .',
    ':field-class cr:dataType sc:Text .',
    ':field-class cr:source :credit-g-arff .',
    
    # File Object - ARFF Distribution
    ':credit-g-arff rdf:type cr:FileObject .',
    ':credit-g-arff rdf:type prov:Entity .',
    ':credit-g-arff rdf:type sc:DataDownload .',
    ':credit-g-arff sc:name "credit-g.arff" .',
    ':credit-g-arff sc:description "Local ARFF format distribution of the German Credit dataset" .',
    ':credit-g-arff sc:encodingFormat "text/arff" .',
    ':credit-g-arff cr:format "ARFF" .',
    ':credit-g-arff prov:wasDerivedFrom :raw_data .',
]

# Usage example:
# engine.insert(data_description_triples, prefixes=prefixes)
