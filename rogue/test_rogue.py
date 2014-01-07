import rogue

def rand_text(arg):
    if arg == 1:
        return """Severe Tropical Cyclone Rewa was a cyclone that affected six countries and killed 22 people on its 28-day journey across the South Pacific Ocean in December 1993 and January 1994. Cyclone Rewa developed from a tropical disturbance on 28 December south of Nauru. After forming, Rewa moved south-southwest through the Solomon Islands, crossing the 160th meridian east from the South Pacific basin into the Australian region. The cyclone began to strengthen steadily and turned southward, paralleling the eastern Australian coast through 31 December. Rewa reached its initial peak intensity as a Category 4 tropical cyclone on 2 January. It maintained this intensity for about 12 hours before an increase in wind shear induced its weakening by 3 January. The cyclone turned southeastward and moved back into the South Pacific basin on 4 January, before it passed over New Caledonia between 5 - 6 January. After affecting New Caledonia, Rewa weakened to a tropical depression and turned northwestward before re-entering the Australian basin on 10 January.
    Over the following days, the cyclone showed signs of restrengthening and executed an elongated cyclonic loop to the southeast of Papua New Guinea. Rewa subsequently entered a phase of quick intensification while proceeding southeastward, peaking in intensity as a Category 5 severe tropical cyclone. It recurved toward the southwest while gradually weakening for several days. Although forecasters had predicted Rewa to make landfall near Mackay, Queensland, the cyclone began interacting with an upper-level trough on 18 January, causing it to divert to the southeast and move along the Queensland coast. Rewa transitioned into an extratropical cyclone on 20 January, with its remnants bringing heavy rain to New Zealand three days later.
    The cyclone caused the deaths of 22 people on its course, affecting parts of the Solomon Islands, Papua New Guinea, Eastern Australia, New Caledonia, Vanuatu and New Zealand. Nine people in a banana dinghy en route to Rossel Island went missing at the height of the storm; they were presumed drowned after wreckage from their boat turned up at the island. In Queensland, three people were killed in traffic accidents caused by the storm, and another fatality occurred when a boy became trapped in a storm pipe. One death took place in New Caledonia, while flooding caused eight drownings in Papua New Guinea. After this usage of the name Rewa, the name was retired."""
    else:
       return """Hoover Dam, once known as Boulder Dam, is a concrete arch-gravity dam in the Black Canyon of the Colorado River, on the border between the US states of Arizona and Nevada. It was constructed between 1931 and 1936 during the Great Depression and was dedicated on September 30, 1935, by President Franklin D. Roosevelt. Its construction was the result of a massive effort involving thousands of workers, and cost over one hundred lives. The dam was controversially named after President Herbert Hoover.
       Since about 1900, the Black Canyon and nearby Boulder Canyon had been investigated for their potential to support a dam that would control floods, provide irrigation water and produce hydroelectric power. In 1928, Congress authorized the project. The winning bid to build the dam was submitted by a consortium called Six Companies, Inc., which began construction on the dam in early 1931. Such a large concrete structure had never been built before, and some of the techniques were unproven. The torrid summer weather and the lack of facilities near the site also presented difficulties. Nevertheless, Six Companies turned over the dam to the federal government on March 1, 1936, more than two years ahead of schedule.
       Hoover Dam impounds Lake Mead, the largest reservoir in the United States by volume.[5] The dam is located near Boulder City, Nevada, a municipality originally constructed for workers on the construction project, about 25 mi (40 km) southeast of Las Vegas, Nevada. The dam's generators provide power for public and private utilities in Nevada, Arizona, and California. Hoover Dam is a major tourist attraction; nearly a million people tour the dam each year. Heavily travelled U.S. 93 ran along the dam's crest until October 2010, when the Hoover Dam Bypass opened."""

def info(score, exp=None):
    if isinstance(exp, float) or isinstance(exp, int):
        print "Score is {}; expected score is {}".format(score, exp)
        return score == exp
    else:
        if not exp:
            print "Score is {}".format(score)
        else:
            print "Score is {}; Expected {}".format(score, exp)
        return -1

if __name__ == "__main__":
    text1 = rand_text(1)
    text2 = rand_text(2)

    #Put in form that is required by rogue
    tmp1 = text1.replace("\n", "")
    tmp2 = text2.replace("\n", "")
    
    tmp1 = tmp1.split(".")
    tmp2 = tmp2.split(".")

    multi_word = lambda x: len(x)>1
    clean1= filter(multi_word, tmp1)
    clean2= filter(multi_word, tmp2)

    s = rogue.similarity2(clean1, clean1)
    info(s, exp=1)
    s = rogue.similarity2(clean1, clean2)
    info(s, exp=0)
    s = rogue.similarity2(clean1+clean2, clean2)
    info(s, "~0.5")
    s = rogue.similarity2(clean1, clean2+clean1[0:3])
    info(s, "~0.1")
    s = rogue.similarity2(clean1, clean1+clean2[0:3])
    info(s, "~0.9")

