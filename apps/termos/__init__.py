def __init__(self, *args, **kwargs):
    super(termos, self).__init__(*args, **kwargs)
    self.fields['valorglobal'].localize = True
    self.fields['valorglobal'].widget.is_localized = True
