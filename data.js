// Sample customer data for Edlio schools and districts
// In production, this would be loaded from an API or MCP
const customers = [
    // California
    { name: "Los Angeles Unified School District", lat: 34.0522, lng: -118.2437, url: "https://lausd.net" },
    { name: "San Francisco Unified School District", lat: 37.7749, lng: -122.4194, url: "https://sfusd.edu" },
    { name: "San Diego Unified School District", lat: 32.7157, lng: -117.1611, url: "https://sandiegounified.org" },
    { name: "Fresno Unified School District", lat: 36.7468, lng: -119.7726, url: "https://fresnounified.org" },
    { name: "Sacramento City Unified School District", lat: 38.5816, lng: -121.4944, url: "https://scusd.edu" },
    { name: "Oakland Unified School District", lat: 37.8044, lng: -122.2712, url: "https://ousd.org" },
    { name: "Long Beach Unified School District", lat: 33.7701, lng: -118.1937, url: "https://lbschools.net" },
    { name: "Elk Grove Unified School District", lat: 38.4088, lng: -121.3716, url: "https://egusd.net" },
    { name: "Santa Ana Unified School District", lat: 33.7455, lng: -117.8677, url: "https://sausd.us" },
    { name: "Riverside Unified School District", lat: 33.9533, lng: -117.3962, url: "https://riversideunified.org" },
    
    // Texas
    { name: "Houston Independent School District", lat: 29.7604, lng: -95.3698, url: "https://houstonisd.org" },
    { name: "Dallas Independent School District", lat: 32.7767, lng: -96.7970, url: "https://dallasisd.org" },
    { name: "Austin Independent School District", lat: 30.2672, lng: -97.7431, url: "https://austinisd.org" },
    { name: "Fort Worth Independent School District", lat: 32.7555, lng: -97.3308, url: "https://fwisd.org" },
    { name: "San Antonio Independent School District", lat: 29.4241, lng: -98.4936, url: "https://saisd.net" },
    { name: "Cypress-Fairbanks Independent School District", lat: 29.9691, lng: -95.6939, url: "https://cfisd.net" },
    { name: "Northside Independent School District", lat: 29.5585, lng: -98.6614, url: "https://nisd.net" },
    { name: "Katy Independent School District", lat: 29.7858, lng: -95.8245, url: "https://katyisd.org" },
    
    // New York
    { name: "New York City Department of Education", lat: 40.7128, lng: -74.0060, url: "https://schools.nyc.gov" },
    { name: "Buffalo Public Schools", lat: 42.8864, lng: -78.8784, url: "https://buffaloschools.org" },
    { name: "Rochester City School District", lat: 43.1566, lng: -77.6088, url: "https://rcsdk12.org" },
    { name: "Yonkers Public Schools", lat: 40.9312, lng: -73.8987, url: "https://yonkerspublicschools.org" },
    { name: "Syracuse City School District", lat: 43.0481, lng: -76.1474, url: "https://syracusecityschools.com" },
    
    // Florida
    { name: "Miami-Dade County Public Schools", lat: 25.7617, lng: -80.1918, url: "https://dadeschools.net" },
    { name: "Broward County Public Schools", lat: 26.1224, lng: -80.1373, url: "https://browardschools.com" },
    { name: "Hillsborough County Public Schools", lat: 27.9506, lng: -82.4572, url: "https://hillsboroughschools.org" },
    { name: "Orange County Public Schools", lat: 28.5383, lng: -81.3792, url: "https://ocps.net" },
    { name: "Palm Beach County School District", lat: 26.7153, lng: -80.0534, url: "https://palmbeachschools.org" },
    { name: "Duval County Public Schools", lat: 30.3322, lng: -81.6557, url: "https://dcps.duvalschools.org" },
    
    // Illinois
    { name: "Chicago Public Schools", lat: 41.8781, lng: -87.6298, url: "https://cps.edu" },
    { name: "Elgin U-46", lat: 42.0354, lng: -88.2826, url: "https://u-46.org" },
    { name: "Rockford Public Schools", lat: 42.2711, lng: -89.0940, url: "https://rps205.com" },
    { name: "Naperville Community Unit School District", lat: 41.7508, lng: -88.1535, url: "https://naperville203.org" },
    
    // Pennsylvania
    { name: "Philadelphia School District", lat: 39.9526, lng: -75.1652, url: "https://philasd.org" },
    { name: "Pittsburgh Public Schools", lat: 40.4406, lng: -79.9959, url: "https://pghschools.org" },
    { name: "Central Bucks School District", lat: 40.3104, lng: -75.1299, url: "https://cbsd.org" },
    
    // Ohio
    { name: "Columbus City Schools", lat: 39.9612, lng: -82.9988, url: "https://ccsoh.us" },
    { name: "Cleveland Municipal School District", lat: 41.4993, lng: -81.6944, url: "https://clevelandmetroschools.org" },
    { name: "Cincinnati Public Schools", lat: 39.1031, lng: -84.5120, url: "https://cps-k12.org" },
    
    // Georgia
    { name: "Gwinnett County Public Schools", lat: 33.9609, lng: -84.0193, url: "https://gcpsk12.org" },
    { name: "Fulton County Schools", lat: 33.7490, lng: -84.3880, url: "https://fultonschools.org" },
    { name: "DeKalb County School District", lat: 33.7956, lng: -84.2279, url: "https://dekalbschoolsga.org" },
    
    // North Carolina
    { name: "Charlotte-Mecklenburg Schools", lat: 35.2271, lng: -80.8431, url: "https://cms.k12.nc.us" },
    { name: "Wake County Public School System", lat: 35.7796, lng: -78.6382, url: "https://wcpss.net" },
    { name: "Guilford County Schools", lat: 36.0726, lng: -79.7920, url: "https://gcsnc.com" },
    
    // Michigan
    { name: "Detroit Public Schools", lat: 42.3314, lng: -83.0458, url: "https://detroitk12.org" },
    { name: "Grand Rapids Public Schools", lat: 42.9634, lng: -85.6681, url: "https://grps.org" },
    { name: "Warren Consolidated Schools", lat: 42.4775, lng: -83.0277, url: "https://wcskids.net" },
    
    // New Jersey
    { name: "Newark Public Schools", lat: 40.7357, lng: -74.1724, url: "https://nps.k12.nj.us" },
    { name: "Jersey City Public Schools", lat: 40.7282, lng: -74.0776, url: "https://jcboe.org" },
    { name: "Paterson Public Schools", lat: 40.9168, lng: -74.1718, url: "https://paterson.k12.nj.us" },
    
    // Virginia
    { name: "Fairfax County Public Schools", lat: 38.8462, lng: -77.3064, url: "https://fcps.edu" },
    { name: "Prince William County Public Schools", lat: 38.7837, lng: -77.5217, url: "https://pwcs.edu" },
    { name: "Virginia Beach City Public Schools", lat: 36.8529, lng: -75.9780, url: "https://vbschools.com" },
    
    // Washington
    { name: "Seattle Public Schools", lat: 47.6062, lng: -122.3321, url: "https://seattleschools.org" },
    { name: "Spokane Public Schools", lat: 47.6588, lng: -117.4260, url: "https://spokaneschools.org" },
    { name: "Tacoma Public Schools", lat: 47.2529, lng: -122.4443, url: "https://tacomaschools.org" },
    
    // Arizona
    { name: "Mesa Public Schools", lat: 33.4152, lng: -111.8315, url: "https://mpsaz.org" },
    { name: "Tucson Unified School District", lat: 32.2226, lng: -110.9747, url: "https://tusd1.org" },
    { name: "Phoenix Union High School District", lat: 33.4484, lng: -112.0740, url: "https://pxu.org" },
    
    // Massachusetts
    { name: "Boston Public Schools", lat: 42.3601, lng: -71.0589, url: "https://bostonpublicschools.org" },
    { name: "Worcester Public Schools", lat: 42.2626, lng: -71.8023, url: "https://worcesterschools.org" },
    { name: "Springfield Public Schools", lat: 42.1015, lng: -72.5898, url: "https://springfieldpublicschools.com" },
    
    // Tennessee
    { name: "Shelby County Schools", lat: 35.1495, lng: -90.0490, url: "https://scsk12.org" },
    { name: "Metro Nashville Public Schools", lat: 36.1627, lng: -86.7816, url: "https://mnps.org" },
    { name: "Knox County Schools", lat: 35.9606, lng: -83.9207, url: "https://knoxschools.org" },
    
    // Maryland
    { name: "Montgomery County Public Schools", lat: 39.0840, lng: -77.1528, url: "https://montgomeryschoolsmd.org" },
    { name: "Prince George's County Public Schools", lat: 38.8303, lng: -76.8455, url: "https://pgcps.org" },
    { name: "Baltimore County Public Schools", lat: 39.4015, lng: -76.6019, url: "https://bcps.org" },
    
    // Wisconsin
    { name: "Milwaukee Public Schools", lat: 43.0389, lng: -87.9065, url: "https://mps.milwaukee.k12.wi.us" },
    { name: "Madison Metropolitan School District", lat: 43.0731, lng: -89.4012, url: "https://madison.k12.wi.us" },
    
    // Colorado
    { name: "Denver Public Schools", lat: 39.7392, lng: -104.9903, url: "https://dpsk12.org" },
    { name: "Jefferson County Public Schools", lat: 39.7247, lng: -105.0988, url: "https://jeffcopublicschools.org" },
    { name: "Aurora Public Schools", lat: 39.7294, lng: -104.8319, url: "https://aurorak12.org" },
    
    // Minnesota
    { name: "Minneapolis Public Schools", lat: 44.9778, lng: -93.2650, url: "https://mpls.k12.mn.us" },
    { name: "St. Paul Public Schools", lat: 44.9537, lng: -93.0900, url: "https://spps.org" },
    { name: "Anoka-Hennepin School District", lat: 45.1975, lng: -93.3877, url: "https://ahschools.us" },
    
    // South Carolina
    { name: "Greenville County Schools", lat: 34.8526, lng: -82.3940, url: "https://greenville.k12.sc.us" },
    { name: "Charleston County School District", lat: 32.7765, lng: -79.9311, url: "https://ccsdschools.com" },
    
    // Alabama
    { name: "Jefferson County School District", lat: 33.5186, lng: -86.8104, url: "https://jefcoed.com" },
    { name: "Mobile County Public School System", lat: 30.6954, lng: -88.0399, url: "https://mcpss.com" },
    
    // Louisiana
    { name: "Jefferson Parish Public School System", lat: 29.9947, lng: -90.1638, url: "https://jpschools.org" },
    { name: "East Baton Rouge Parish School System", lat: 30.4515, lng: -91.1871, url: "https://ebrschools.org" },
    
    // Kentucky
    { name: "Jefferson County Public Schools", lat: 38.2527, lng: -85.7585, url: "https://jefferson.kyschools.us" },
    { name: "Fayette County Public Schools", lat: 38.0406, lng: -84.5037, url: "https://fcps.net" },
    
    // Oregon
    { name: "Portland Public Schools", lat: 45.5152, lng: -122.6784, url: "https://pps.net" },
    { name: "Salem-Keizer School District", lat: 44.9429, lng: -123.0351, url: "https://salkeiz.k12.or.us" },
    
    // Oklahoma
    { name: "Oklahoma City Public Schools", lat: 35.4676, lng: -97.5164, url: "https://okcps.org" },
    { name: "Tulsa Public Schools", lat: 36.1540, lng: -95.9928, url: "https://tulsaschools.org" },
    
    // Connecticut
    { name: "Hartford Public Schools", lat: 41.7658, lng: -72.6734, url: "https://hartfordschools.org" },
    { name: "New Haven Public Schools", lat: 41.3083, lng: -72.9279, url: "https://nhps.net" },
    
    // Utah
    { name: "Granite School District", lat: 40.6851, lng: -111.9383, url: "https://graniteschools.org" },
    { name: "Jordan School District", lat: 40.5621, lng: -111.9297, url: "https://jordandistrict.org" },
    
    // Iowa
    { name: "Des Moines Public Schools", lat: 41.5868, lng: -93.6250, url: "https://dmschools.org" },
    { name: "Cedar Rapids Community School District", lat: 41.9779, lng: -91.6656, url: "https://crschools.us" },
    
    // Nevada
    { name: "Clark County School District", lat: 36.1699, lng: -115.1398, url: "https://ccsd.net" },
    { name: "Washoe County School District", lat: 39.5296, lng: -119.8138, url: "https://washoeschools.net" },
    
    // Kansas
    { name: "Wichita Public Schools", lat: 37.6872, lng: -97.3301, url: "https://usd259.org" },
    { name: "Olathe Public Schools", lat: 38.8814, lng: -94.8191, url: "https://olatheschools.org" },
    
    // Arkansas
    { name: "Little Rock School District", lat: 34.7465, lng: -92.2896, url: "https://lrsd.org" },
    { name: "Springdale School District", lat: 36.1867, lng: -94.1288, url: "https://sdale.org" },
    
    // Mississippi
    { name: "Jackson Public School District", lat: 32.2988, lng: -90.1848, url: "https://jackson.k12.ms.us" },
    { name: "DeSoto County School District", lat: 34.9668, lng: -89.9937, url: "https://desotocountyschools.org" },
    
    // New Mexico
    { name: "Albuquerque Public Schools", lat: 35.0853, lng: -106.6056, url: "https://aps.edu" },
    { name: "Las Cruces Public Schools", lat: 32.3199, lng: -106.7637, url: "https://lcps.net" },
    
    // Nebraska
    { name: "Omaha Public Schools", lat: 41.2565, lng: -95.9345, url: "https://ops.org" },
    { name: "Lincoln Public Schools", lat: 40.8136, lng: -96.7026, url: "https://lps.org" },
    
    // West Virginia
    { name: "Kanawha County Schools", lat: 38.3498, lng: -81.6326, url: "https://kcs.kana.k12.wv.us" },
    { name: "Berkeley County Schools", lat: 39.4560, lng: -77.9639, url: "https://berkeleycountyschools.org" },
    
    // Idaho
    { name: "Boise School District", lat: 43.6150, lng: -116.2023, url: "https://boiseschools.org" },
    { name: "West Ada School District", lat: 43.5854, lng: -116.3542, url: "https://westada.org" },
    
    // Hawaii
    { name: "Hawaii Department of Education", lat: 21.3099, lng: -157.8581, url: "https://hawaiipublicschools.org" },
    
    // New Hampshire
    { name: "Manchester School District", lat: 42.9956, lng: -71.4548, url: "https://mansd.org" },
    { name: "Nashua School District", lat: 42.7654, lng: -71.4676, url: "https://nashua.edu" },
    
    // Maine
    { name: "Portland Public Schools", lat: 43.6591, lng: -70.2568, url: "https://portlandschools.org" },
    { name: "Bangor School Department", lat: 44.8012, lng: -68.7778, url: "https://bangorschools.net" },
    
    // Montana
    { name: "Billings Public Schools", lat: 45.7833, lng: -108.5007, url: "https://billingsschools.org" },
    { name: "Great Falls Public Schools", lat: 47.5002, lng: -111.3008, url: "https://gfps.k12.mt.us" },
    
    // Delaware
    { name: "Christina School District", lat: 39.7459, lng: -75.5466, url: "https://christinak12.org" },
    { name: "Red Clay Consolidated School District", lat: 39.7801, lng: -75.5508, url: "https://redclayschools.com" },
    
    // South Dakota
    { name: "Sioux Falls School District", lat: 43.5446, lng: -96.7311, url: "https://sf.k12.sd.us" },
    { name: "Rapid City Area School District", lat: 44.0805, lng: -103.2310, url: "https://rcas.org" },
    
    // North Dakota
    { name: "Fargo Public Schools", lat: 46.8772, lng: -96.7898, url: "https://fargo.k12.nd.us" },
    { name: "Bismarck Public Schools", lat: 46.8083, lng: -100.7837, url: "https://bismarckschools.org" },
    
    // Rhode Island
    { name: "Providence Public School District", lat: 41.8240, lng: -71.4128, url: "https://providenceschools.org" },
    { name: "Warwick Public Schools", lat: 41.7001, lng: -71.4162, url: "https://warwickschools.org" },
    
    // Vermont
    { name: "Burlington School District", lat: 44.4759, lng: -73.2121, url: "https://bsdvt.org" },
    { name: "South Burlington School District", lat: 44.4669, lng: -73.1710, url: "https://sbschools.net" },
    
    // Wyoming
    { name: "Laramie County School District #1", lat: 41.1400, lng: -104.8202, url: "https://laramie1.org" },
    { name: "Natrona County School District", lat: 42.8501, lng: -106.3252, url: "https://natronaschools.org" },
    
    // Alaska
    { name: "Anchorage School District", lat: 61.2181, lng: -149.9003, url: "https://asdk12.org" },
    { name: "Fairbanks North Star Borough School District", lat: 64.8378, lng: -147.7164, url: "https://k12northstar.org" },
    { name: "Matanuska-Susitna Borough School District", lat: 61.5816, lng: -149.4394, url: "https://matsuk12.us" }
];