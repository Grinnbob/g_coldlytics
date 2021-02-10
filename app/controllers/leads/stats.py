class SpreadSheetStats():
    def __init__(self):
        self.stats = {}

    def reset_stats(self):
        self.stats = {}

    def inc_stats_metric(self,
                          sheet,
                          metric):
        if not self.stats.get(sheet.id):
            self.stats[sheet.id] = {
                'sheet_title' : sheet.title
            }

        if not self.stats[sheet.id].get(metric):
            self.stats[sheet.id][metric] = 1
        else:
            self.stats[sheet.id][metric] += 1

    def set_stats_metric(self,
                         sheet,
                         metric,
                         value):
        if not self.stats.get(sheet.id):
            self.stats[sheet.id] = {
                'sheet_title' : sheet.title
            }

        self.stats[sheet.id][metric] = value

    def raw_stats(self):
        return self.stats

class CrmUploadStats():
    def __init__(self):
        self.stats = {}

    def reset_stats(self):
        self.stats = {}

    def inc_stats_metric(self,
                         metric):
        if not self.stats.get(metric):
            self.stats[metric] = 1
        else:
            self.stats[metric] += 1

    def set_stats_metric(self,
                         metric,
                         value):
        self.stats[metric] = value

    def raw_stats(self):
        return self.stats
