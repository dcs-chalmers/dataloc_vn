def violinify(ax_object,data,positions=None,widths=None,color='black', labeled_median=False, labels_median=[]):

    violinwidths = 0.5 if widths == None else widths


    def stradivari(some_violinplot,some_color):
        for pc in some_violinplot['bodies']:
            pc.set_facecolor(some_color)
            pc.set_alpha(0.25)
        for key in some_violinplot.keys():
            if key not in ['bodies','cmins','cmaxes']:
                pc = some_violinplot[key]
                pc.set_color(some_color)
                pc.set_linewidth(1)

    parts = ax_object.violinplot(data,positions=positions,widths=violinwidths,
                                    showextrema=False,showmeans=False)
    stradivari(parts,color)
    bp_dict = ax_object.boxplot(data,positions=positions,widths=widths,
                        showfliers=False,
                        medianprops=dict(color=color),
                        boxprops=dict(color='None'),
                        whiskerprops=dict(color='None'),
                        capprops=dict(color='None'))

    if labeled_median:

        for line, label in zip(bp_dict['medians'], labels_median):
        # get position data for median line
            x_left, _ = line.get_xydata()[0]    # left edge of median line
            x_right, y  = line.get_xydata()[1]  # right edge of median line

            x = (x_right + x_left)/2
        # overlay median value
            ax_object.text(x, y, label,
                horizontalalignment='center', verticalalignment='bottom', # draw above, centered
                fontsize=8, rotation=90,
                alpha=0.7)