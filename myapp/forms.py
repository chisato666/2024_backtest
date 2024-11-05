from django import forms

class BacktestForm(forms.Form):
    symbol = forms.CharField(max_length=10)
    score_threshold = forms.FloatField()
    tp_percent = forms.FloatField(label="Take Profit (%)")
    sl_percent = forms.FloatField(label="Stop Loss (%)")
    timeframe = forms.ChoiceField(choices=[('1h', '1 Hour'), ('4h', '4 Hours'), ('Day1', '1 Day'), ('Week1', '1 Week')])
    start_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    end_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))