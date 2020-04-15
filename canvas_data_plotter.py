
import matplotlib.pyplot as plt
from matplotlib import cm
import matplotlib.gridspec as gridspec
import numpy as np

def make_figure(color, data):
    
    # Some placeholder code to return a figure
    fig = plt.figure(figsize=(8, 5*len(data['assignments'])))
    gs = gridspec.GridSpec(len(data['assignments']), 1)
    
    pts = data['section_pts']
    pts.extend(['Unsubmitted','Ungraded'])
    cs = list(cm.Spectral(np.arange( (len(pts)-2)) / (len(pts)-2) ) ) 
    cs.extend(['k', 'gray'])

    for PLOTi, assignment in enumerate(data['assignments']):

        ax = fig.add_subplot(gs[PLOTi, 0])
        bins = assignment['ammount_graded']
        legend_labels = assignment['graders']
        
        colors = []
        for l in legend_labels:
            colors.append(cs[np.where(np.asarray(pts) == l)[0][0]])
            
        wedges, texts = ax.pie(bins, colors=colors, wedgeprops=dict(width=0.5), startangle=-40)

        ### this makes cute little boxes with percentage breakdowns to label the slices
        ### its gross and confusing just ignore it
        bbox_props = dict(boxstyle="square,pad=0.3", fc="w", ec="k", lw=0.72)
        kw = dict(arrowprops=dict(arrowstyle="-"), bbox=bbox_props, zorder=0, va="center")

        for i, p in enumerate(wedges):

            ang = (p.theta2 - p.theta1)/2. + p.theta1

            y = np.sin(np.deg2rad(ang))
            x = np.cos(np.deg2rad(ang))

            horizontalalignment = {-1: "right", 1: "left"}[int(np.sign(x))]
            connectionstyle = "angle,angleA=0,angleB={}".format(ang)
            kw["arrowprops"].update({"connectionstyle": connectionstyle})

            if bins[i] != 0:
                if sum(bins) != 0:
                    ax.annotate('{0:.2f}%'.format((bins[i]/sum(bins))*100), xy=(x, y), xytext=(1.35*np.sign(x), 1.4*y), fontsize = 12, horizontalalignment=horizontalalignment, **kw)
                else:
                    ax.annotate('{0:.2f}%'.format(0), xy=(x, y), xytext=(1.35*np.sign(x), 1.4*y), fontsize = 12, horizontalalignment=horizontalalignment, **kw)

        ### produce the legend and format it
        legend = ax.legend(labels = legend_labels, fontsize=10, loc='center',facecolor='w', framealpha=1, title = assignment['assignment_name'], edgecolor = 'k')
        legend.get_title().set_fontsize(13)
        plt.suptitle(f"Grading Breakdown \n{data['name']} \nProfessor {data['prof_name']}")
    gs.update(left=0.25, right=0.75, top=0.95, bottom=0.02, wspace=0.02, hspace=0.1)

    return fig    
    