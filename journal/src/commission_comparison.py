
import pandas as pd
import plotly.graph_objects as go

def ibkrCommission(q:float, p:float, type:str='tiered', monthly_q:float=None):
    if type in ['tiered', 'fixed']:
        if type == 'tiered':
            if monthly_q is None:
                raise ValueError('When the type is "tiered" you must specify the "monthly_q" with the expected monthly traded quantity.')

            mi = 0.35 # Min commission 0.35$
            ma = 0.01 # Máx commission 1%

            # Add specific fees:
            # FINRA TAF: $0.000166
            # Pass-through NYSE: 0.000175 and FINRA: 0.00056 of base commission (despreciable)
            # Clearing:$ 0.0002 
            # CAT: $0.000033
            # Remove liquidity: $0.003
            if monthly_q <= 300000:
                c = q*0.0035
            elif 300000 < monthly_q and monthly_q <= 3000000:
                c = q*0.002
            elif 3000000 < monthly_q and monthly_q <= 20000000:
                c = q*0.0015
            elif 20000000 < monthly_q and monthly_q <= 100000000:
                c = q*0.001
            else:
                c = q*0.0005

            fee = q * (0.000166 + 0.0002 + 0.000033) + 0.003
                
        elif type == 'fixed':
            mi = 1 # Min commission 1$
            ma = 0.01 # Máx commission 1%
            c = q*0.005
            fee = 0
            
        return min(max(mi, c), q*p*ma) + fee
    else:
        raise ValueError('The type must be "tiered" or "fixed"!')

fixed = []
tiered = []
q = 1000
while q < 100000:
    for p in [0.5, 1.5, 5.5, 10, 20.5, 50, 100, 300, 500, 1000]:
        fixed.append({'price': p, 'quantity': q, 'comm': ibkrCommission(q=q, p=p, type='fixed')})
        tiered.append({'price': p, 'quantity': q, 'comm': ibkrCommission(q=q, p=p, type='tiered', monthly_q=q*20)})
    q *= 2

df_fixed = pd.DataFrame(fixed)
df_tiered = pd.DataFrame(tiered)

# Pivot para obtener la matriz de comisiones
z_fixed = df_fixed.pivot(index='quantity', columns='price', values='comm').sort_index()
z_tiered = df_tiered.pivot(index='quantity', columns='price', values='comm').sort_index()

fig = go.Figure()

fig.add_trace(go.Surface(
    z=z_fixed.values,
    x=z_fixed.columns,
    y=z_fixed.index,
    colorscale='Blues',
    name='Fixed'
))

fig.add_trace(go.Surface(
    z=z_tiered.values,
    x=z_tiered.columns,
    y=z_tiered.index,
    colorscale='Reds',
    opacity=0.7,
    name='Tiered'
))

fig.update_layout(
    title='Comisiones IBKR: Fixed vs Tiered',
    scene=dict(
        xaxis_title='Precio',
        yaxis_title='Cantidad',
        zaxis_title='Comisión'
    ),
    legend=dict(x=0.8, y=0.9)
)

fig.show()