class CloseComLeadSerializer():
    def __init__(self,
                 organization,
                 internal_status):
        self.organization = organization
        self.internal_status = internal_status

    def serialize_leads_array(self,
                              df,
                              mapping):
        leads = {}

        lead_fields = mapping['lead_fields']
        contact_fields = mapping['contact_fields']

        filtered_columns = list(lead_fields.keys())
        filtered_columns.extend(list(contact_fields.keys()))
        filtered_columns = list(set(filtered_columns))

        #remove all fields that are not in mapping
        filtered_df = df[filtered_columns]
        rows = filtered_df.to_dict('records')

        # invert {"column title" : "field name"}  to {"field_name" : "column_title"}
        inv_contact_fields = {v: k for k, v in contact_fields.items()}
        inv_lead_fields = {v: k for k, v in lead_fields.items()}

        # remember lead name column
        lead_name_column = inv_lead_fields['name']
        del inv_lead_fields['name']

        # REQUIRED SCHEMA FIELDS:
        # name = fields.StringField()
        # organization = fields.StringField(required=True)
        # internal_status = fields.StringField(required=True)
        # contacts = fields.ListField(fields.DictField())
        # lead_fields = fields.DictField()

        for row in rows:
            contact = self.serialize_contact(row,
                                            inv_contact_fields)


            #get lead name and create lead if it's not exist
            lead_name = str(row[lead_name_column]).strip()
            if not leads.get(lead_name):
                leads[lead_name] = self.create_lead_fields(lead_name)


            leads[lead_name] = self.update_lead_fields(lead=leads[lead_name],
                                                       data=row,
                                                       inv_lead_fields=inv_lead_fields,
                                                       contact=contact)

        return leads

    #will create contact (for closecom spreadsheet_uploader) from raw data
    def serialize_contact(self,
                          data,
                          inv_contact_fields):
        contact = {}


        # get contact's values which we want to map
        for k, v in inv_contact_fields.items():
            if k == 'email':
                if not contact.get('emails'):
                    contact['emails'] = []

                contact['emails'].append({'type': 'office',
                                          'email': str(data[v]).strip().lower()})
            else:
                contact[k] = str(data[v]).strip()

        return contact


    #will create or update lead with raw data
    def create_lead_fields(self,
                           lead_name):
        lead = {}

        lead['name'] = lead_name
        lead['contacts'] = []

        # system DB fields
        lead['internal_status'] = self.internal_status
        lead['organization'] = self.organization
        lead['lead_fields'] = {}

        return lead

    def update_lead_fields(self,
                           lead,
                           data,
                           inv_lead_fields,
                           contact):

        for k, v in inv_lead_fields.items():
            if not lead['lead_fields'].get(k) or data[v]:
                lead['lead_fields'][k] = str(data[v]).strip()

        if contact:
            lead['contacts'].append(contact.copy())

        return lead