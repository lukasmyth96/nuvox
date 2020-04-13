
import numpy as np
from matplotlib import pyplot as plt


def plot_swype_probabilities(swype, top_n=10):
    """
    Plot bar chart of trace, language and joint probabilities for suggestions in swype
    Parameters
    ----------
    swype: nuvox.swype.Swype
    top_n: int
        how many words to show
    """

    # data to plot
    words = sorted(swype.word_to_joint_prob.keys(), key=lambda word: swype.word_to_joint_prob[word], reverse=True)[:top_n]
    trace_probs = [swype.word_to_trace_prob[w] for w in words] if swype.word_to_trace_prob else None
    lang_probs = [swype.word_to_language_prob[w] for w in words] if swype.word_to_language_prob else None
    joint_probs = [swype.word_to_joint_prob[w] for w in words] if swype.word_to_joint_prob else None

    # create plot
    index = np.arange(min(len(words), top_n))
    bar_width = 0.25
    opacity = 0.9

    if trace_probs:

        bar1 = plt.bar(index, trace_probs, bar_width,
                       alpha=opacity,
                       color='b',
                       label='trace algo probs')

    if lang_probs:
        bar2 = plt.bar(index + bar_width, lang_probs, bar_width,
                       alpha=opacity,
                       color='g',
                       label='language model probs')

    if joint_probs:
        bar3 = plt.bar(index + 2 * bar_width, joint_probs, bar_width,
                       alpha=opacity,
                       color='r',
                       label='weighted joint prob')

    plt.xlabel('Word')
    plt.ylabel('Prob')
    plt.ylim(0, 1)
    plt.title('Swype probability diagnostic')
    plt.xticks(index + bar_width, words, rotation=45)
    plt.legend()

    plt.tight_layout()
    plt.show()


if __name__ == '__main__':
    """ Testing """
    import os
    from nuvox.utils.io import pickle_load
    from definition import ROOT_DIR

    sess = pickle_load(os.path.join(ROOT_DIR, 'analytics_data', '2020_04_10_T17_18_19.pkl'))
    plot_swype_probabilities(sess[0])
    print('stop here to experiment')
