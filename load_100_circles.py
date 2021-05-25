# Load 100 Circles data from URL.

import argparse
import datetime
import json
from pathlib import Path
import urllib.parse
import urllib.request

import utils


parser = argparse.ArgumentParser()
parser.add_argument("wikitree_id")
args = parser.parse_args()

# utils.log("Loading URL")
# params = urllib.parse.urlencode({"WikiTreeID": args.wikitree_id})
# url = f"https://wikitree.sdms.si/function/WT100Circles/Tree.json?{params}"
# with urllib.request.urlopen(url) as resp:
#   data_text = resp.read().decode("ascii")

data_text = """{
"request": {

"debug": 2,

"startUserID": 19440571

},


"tree": {
"size": "22621144",
"generations": "95",
"furthest profiles": [29053758,29053769]
}
,"debug": {
"generations": 95,
"steps": ["0:1:1:0","1:3:4:3","2:11:15:21","3:26:41:95","4:92:133:373","5:266:399:1524","6:444:843:4430","7:773:1616:8869","8:969:2585:17516","9:1339:3924:26089","10:2049:5973:40543","11:3752:9725:63906","12:8191:17916:109060","13:20304:38220:215002","14:56875:95095:506000","15:149459:244554:1366641","16:339190:583744:3650271","17:619661:1203405:8737193","18:927123:2130528:17473520","19:1268761:3399289:29426484","20:1649408:5048697:44742654","21:1953668:7002365:63643689","22:2067181:9069546:84628744","23:1987515:11057061:105188858","24:1804437:12861498:123652081","25:1607730:14469228:139858538","26:1425705:15894933:154465725","27:1235435:17130368:167574443","28:1052940:18183308:178888060","29:884280:19067588:188408105","30:728548:19796136:196294937","31:589936:20386072:202719387","32:464287:20850359:207827358","33:363505:21213864:211792227","34:285756:21499620:214826293","35:220790:21720410:217196213","36:171198:21891608:218982062","37:133794:22025402:220369088","38:106163:22131565:221442538","39:85460:22217025:222302607","40:68993:22286018:222991877","41:56861:22342879:223544937","42:46764:22389643:223997988","43:37834:22427477:224367582","44:32198:22459675:224672350","45:26246:22485921:224925881","46:22469:22508390:225129989","47:18662:22527052:225308593","48:16433:22543485:225454305","49:13365:22556850:225581442","50:11474:22568324:225676691","51:9410:22577734:225765397","52:6896:22584630:225839267","53:5482:22590112:225890840","54:4135:22594247:225931655","55:3488:22597735:225964388","56:3025:22600760:225991488","57:2471:22603231:226015484","58:2011:22605242:226034360","59:1627:22606869:226050542","60:1611:22608480:226063392","61:1247:22609727:226077850","62:1106:22610833:226086468","63:996:22611829:226094900","64:1008:22612837:226102870","65:947:22613784:226110726","66:1113:22614897:226117973","67:1018:22615915:226126758","68:939:22616854:226133258","69:897:22617751:226138868","70:734:22618485:226143407","71:549:22619034:226147090","72:444:22619478:226149713","73:390:22619868:226152209","74:301:22620169:226153775","75:205:22620374:226155016","76:162:22620536:226155969","77:134:22620670:226156557","78:146:22620816:226157524","79:100:22620916:226158187","80:80:22620996:226158817","81:27:22621023:226159256","82:32:22621055:226159397","83:36:22621091:226160034","84:29:22621120:226160819","85:7:22621127:226161156","86:1:22621128:226161164","87:1:22621129:226161166","88:2:22621131:226161168","89:1:22621132:226161174","90:1:22621133:226161176","91:5:22621138:226161178","92:2:22621140:226161224","93:2:22621142:226161228","94:2:22621144:226161233","95:0"]
}
}"""

print("Data:", data_text)

utils.log("Parsing JSON")
data = json.loads(data_text)

utils.log("Extracting circle sizes")
circle_sizes = []
for step in data["debug"]["steps"]:
  # Format: circle_num ":" circle_size ":" cumulative_size ":" ???
  this_size = step.split(":")[1]
  circle_sizes.append(int(this_size))



utils.log("Writing results")
date = datetime.date.today().strftime("%Y-%m-%d")
with open(Path("results", "circles", f"{args.wikitree_id}_{date}.json"), "w") as f:
  json.dump({args.wikitree_id: circle_sizes}, f)

utils.log("Finished")
