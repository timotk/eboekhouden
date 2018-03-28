def hours_summary(df):
    return [('sum', df['Aantal uren'].sum()),
           ('mean', df[['Datum', 'Aantal uren']].groupby('Datum').sum().mean().iloc[0]),
           ('median', df[['Datum', 'Aantal uren']].groupby('Datum').sum().median().iloc[0])]

def hours_per_project(df):
    return df[['Project','Aantal uren']].groupby('Project').sum()
