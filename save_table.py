import matplotlib.pyplot as plt
import pandas as pd

def save_table_as_image(self):
        
        data = {
            e: [self.table[s].get(e, '') for s in self.S] + 
            [self.table[s].get(e, '') for s in [s + a for s in self.S for a in self.alphabet if s + a not in self.S]]
            for e in self.E
        }
        rows = self.S + [s + a for s in self.S for a in self.alphabet if s + a not in self.S]
        df = pd.DataFrame(data, index=rows)

        df.index = df.index.map(lambda s: s if s else "ε")
        df.columns = [col if col else "ε" for col in df.columns]

        fig, ax = plt.subplots(figsize=(10, 8))

        colors = [["#b3cde3" if row in self.S or row == "ε" else "#f2e2d2" for _ in df.columns] for row in df.index]

        table = plt.table(
            cellText=df.values,
            rowLabels=df.index,
            colLabels=df.columns,
            cellColours=colors,
            cellLoc='center',
            loc='center'
        )
        
        table.auto_set_font_size(False)
        table.set_fontsize(10)
        table.scale(1.5, 1.5)

        for key, cell in table.get_celld().items():
            cell.set_edgecolor("grey") 
            cell.set_linewidth(0.3)

        plt.axis('off')  
        plt.savefig("observation_table_enhanced.png", bbox_inches='tight')
        print("Saved the enhanced observation table as 'observation_table_enhanced.png'.")
