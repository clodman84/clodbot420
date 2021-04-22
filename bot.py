import pickle
import random
from datetime import datetime

import discord
import gspread
import requests
from discord.ext import tasks
from oauth2client.service_account import ServiceAccountCredentials


scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']  # this part requests the api
creds = ServiceAccountCredentials.from_json_keyfile_name('Kepler.json', scope)
client = gspread.authorize(creds)
Arsenal = client.open('Enriching Weapons Grade Uranium (Responses)').sheet1

client = discord.Client()

intros = []
phrases = ['Yes, uh', 'Why am I doing this?', 'Romantic dude cums on rose',
           'Spongeknob Squarenuts', 'Explosive beaver hammering', "Thor thunder smacks yoda's sopping wet pussy "
                                                                  "with his throbbing lightsaber as he screams "
                                                                  "420 blaze it faggot ",
           'Old ass woman that is about to die gets fucked',
           'Emo couple wants to fuck more than they want to die', 'Big hairy Gustavo whacks his gack',
           "You've Got Midget - Scene 1", 'Lemon stealing whore', 'Baby thrown off balcony',
           'Sleepwalking stepbrother', 'Edward penis hands', 'Retarded goth jerking off while crying',
           'Adolf Hitler painting destroyed by big black cock', "It's okay mom, I'm here", 'Pikachu cums',
           'Asscream sundae', 'Young hot redhead pisses on everything in the room', 'Ten wet piss scenes',
           'Dumb cunt eating ice cream', "Tiger's Wood", "I don't know WTF is going on, but the frog fucks good",
           'Meme orgy gets nasty', 'Please Santa, drill my ass', "The taste of grandma's furburger",
           'Not the Cosbys, but close enough', 'Phineas and Ferb', 'Bald bitch gets wild with snakes and',
           'Insert two apple in ass', 'Black cock down', 'Straight male gets drilled by corn',
           'Willy Wonka and the Fudge Packing Factory', 'Sausage and spaghetti dinner', "Mom's spaghetti",
           'The Prune Brothers', 'Pretty boy pees, farts and flexes his bunghole', 'Engulfing a delectable willy',
           'Her black stepdads retarded cock', 'The Gimp and the Retard', "Anna Nicole Smith's retarded daughter",
           'Amputee smears herself with sauce', 'Amputee', 'Toy story hentai', 'Forrest Hump', "Schindler's Fist",
           'The Flintbones', 'Good Will Humping', 'Shrek', 'Walt Disney-4',
           "Whorey Potter and the Sorcerer's Balls", 'Cake farts', 'Karate girl foot sniffing', 'Scoopy Doo',
           'Sonic having orgasms', 'A Chinese fish looks like penis', 'Reporter gets banged by terrorists',
           'Kung fu power sex', 'Fisting wars tale of the lost arm', 'Getting hole punched at an office party',
           'The sperm burger extra mayo-free', 'Hot blonde fucked by a gargoyle',
           'Hot redhead performing super hot solo', 'Adventures of the Fart Bitches',
           'My brother spying on the neighbor, haha', "69420", "oh yeah babe",
           "shovel", "cheese", "dick",
           "my schloppity schlong", "my big benis", "Shaatacharya Gupta Mourya", "ballsacks dipped in sauce",
           "nice cock bro", "mamma mia khalifa", "lolo", "monke", "cheese", "dumbfuck", "cunt",
           "your project is ruined yeah", ]
sentences = [
    'Kill yourself\nPlease please kill yourself\nYou should really kill yourself\nPlease please kill '
    'yourself\nYou should really\nPoo poo, pee pee, penis and vagina\nWomen with dicks and weak men with '
    'vaginas\nSo fucking delicate like mommys fine china\nIf you have complaints please wait your turn and '
    'line up\nI got a message for these little fags trynna\nBe a mommys boy and a teachers pet, pimple face, '
    'asswipe\nLooking like they just had a gyne-cologist\nStick five fingers in your ass, no lube\nSo '
    'whatcha gonna do?\nIf youre number one, shove it up your ass and make it number Two (Oh)\nLadies '
    'getting mad in the comments, and Im hearing it\nYou think it was a typo with these red lines and '
    'periods\n(Oooh)\nHa ha no comma, bitches with their self esteem get out of the sauna\nMy shit lies in '
    'the sewers, closing the hatch\nI only joke about diseases and reference that only you can catch\n(Ew, '
    'oh my god)\nAnd if you think youre fucking grown up\nKeep breathing heavy with your keyboard and '
    'fedora\nHands around your dick with the kung-fu grip\nStroking back and forth to My Little Pony clips '
    'bitch\nGo outside and ride a bike or something\nAnd get laughed at by kids to remind you that you are '
    'nothing\nAnd then, get hit by every car or truck that ever passes\nYour life flashes before your eyes, '
    'oh wait, its your Google Glasses\nNever mind faggot, just pick your ass up and take you to the closest '
    'sign faggot\nIm not done yet, you get up and you go home\nSit at your computer and open up Google '
    'Chrome\nAnd then look at tutorials on how to hang yourself at home\nAnd then you can hang yourself\n(Is '
    'that the end of the story?\nHa ha ha ha ha, no son)\nKill yourself, please please kill yourself\nYou '
    'should really kill yourselves\nPlease please kill yourself\nYou should really kill yourselves',
    ' Donkey Kong fucks King Kongs ding dong. YOLO swag bro.',
    'Tom and I can I get back to me to go someware, bloody bloody arse.',
    'The movie tells the tale of a beautiful young woman whose life is turned around when her ex-porn star '
    'dad is made (by the producers) to cast her as the lead in his latest x-rated film. A devastating '
    'testimony of the rise and fall of the Dick In SON family values, an existentialist journey where habit '
    'and cruelty are only separated by life and death.',
    ' Suck my glorious cock!\n\nSuck my glorious cock!\n\nIts not a proper title for a movie!',
    '\nShut the fuck up\nYoure a fucking cunt\nShut the fuck up\nYoure a stupid cunt, suck my dick\nShut the '
    'fuck up\nStop being a fucking cunt\nShut the fuck up\nNobody even wants you here',
    'What?\nI just want to let you know, youre a stupid fucking cunt\nGo ahead and run your mouth, pussy, '
    'I dont give a fuck\nYoure a stupid piece of shit, youre a stupid fucking bitch\nGet the fuck up off my '
    'dick, get the fuck up off my dick, like\nPlease end your fucking life, please end your fucking life\nI '
    'really gotta emphasize, no one cares if youre alive',
    'Youre a fucking penis-hole, grab a dick and eat it whole\nI need to know if you were dropped when you '
    'were just a fetus though',
    'Shut the fuck up\nStop being a fucking cunt\nShut the fuck up\nNobody even wants you here\nIm not crazy, '
    'I just do it all because I can, boy\nI hope you fucking die in a high-speed car crash',
    'I hope you fucking fall head-first and get your neck cracked\nI hope you have some beautiful children '
    'that die from cancer\nI hope you catch Zika when your wife gets pregnant\nI hope you win the lottery '
    'and die the next day\nAnd your daughter has to see you getting lowered in your grave\n\nLike, uh, '
    'ooh- that was a little dark\nIm sorry. Tha-that was a little dark. Very poor taste\nShut the fuck up\nI '
    'shouldnt have said that\nYoure a fucking cunt',
    'I love hentai\nI need hentai in my life\nAll day all day I love hentai\nI need hentai in my life, '
    'yuh\nI love hentai\nI need hentai in my life',
    ' Suck my glorious cock!\n\nSuck my glorious cock!\n\nIts not a proper title for a movie!']
sites = ["oh yeah ",
         "Vennu Mallesh it's my life", "shart festival", "benis power",
         'ViewGals', 'JPEGWorld', 'PicHunter', 'NakedPornPics', '18AsianTube', 'Zenra', 'BDSMstreak', 'PunishBang',
         'Clips4Sale', 'ZZCartoon', 'HentaiHaven', 'HentaiCore', 'Hentaigasm', 'Fakku', 'Gelbooru', 'HentaiSea',
         'HentaiPulse', 'Porcore', 'CartoonPorno', 'Sankakucomplex', 'Hentai-Foundry', 'EggPornComics', 'VrPorn',
         'VRBangers', 'VRSmash', 'BadoinkVR', 'WankzVR', 'CzechVR', 'SexLikeReal', 'VirtualRealPorn', 'GayMaleTube',
         'ManPorn', 'YouPornGay', 'GayFuror', 'ZZGays', 'JustUsBoys', 'MyPornGay', 'Babepedia', 'TubePornStars',
         'StasyQ', 'TheChive', 'HotSouthIndianSex',
         'ShemaleHD', 'AnyShemale', 'AShemaleTube', 'Tranny', 'TGTube', 'BestTrannyPornSites',
         '69Games', 'GamCore', 'GamesOfDesire', 'JerkDolls', 'HooligApps', 'cunt', 'Cheese',
         'Desimurga.com', ' PICKLE', ' Chungus', ' Penis stone', ' Big Dick Energy',
         ' Pussy ', ' Nyesss ', ' Dick ', ' Cunt ', 'Randi University of the Ten Commandments',
         'Randi Wright brothers', '1) indlansex.net', '2) 3rat.com', '3) 4hen.com', '4) africansexvideos.net',
         '5) bananabunny.com', '6) cutepornvideos.com', '7) desimurga.com', '8) desisexclips.com', '9) dslady.com',
         '10) eroticperfection.com', '11) es.porn.com', '12) gaypornium.com', '13) gracefulnudes.com',
         '14) hot-dates.info', '15) hqlinks.net', '16) how-do-you-produce-more-seminal-fluid.semenaxx.org',
         '17) indianporntube.xxx', '18) indiansex4u.com', '19) jav-porn.net', '20) kirtu.com', '21) legalporno.com',
         '22) luboeporno.com', '23) mypornbookmarks.com', '24) pinkythekinky.com', '25) pornfromczech.com',
         '26) sexsex.hu', '27) sexxxxi.com', '28) shemale.asia', '29) teengayporntube.com', '30) thefreecamsecret.com',
         '31) theporndude.com', '32) momsteachsex.com', '33) videos.petardas.com', '34) www.xvideos.com',
         '35) www.89.com', '36) www.adultsextube.com', '37) www.alohatube.com', '38) www.analsexstars.com',
         '39) www.babosas.com', '40) www.bomnporn.com', '41) www.brazzers.com', '42) www.callboyindia.com',
         '43) en.cam4.co', '44) en.cam4.com.br', '45) www.cam4.in', '46) www.cholotube.com', '47) www.cliphunter.com',
         '48) www.cullosgratis.com.ve', '49) www.cumlouder.com', '50) www.darering.com', '51) www.drtuber.com',
         '52) www.epicporntube.com', '53) www.eporner.com', '54) www.fapto.xxx', '55) www.flirt4free.com',
         '56) www.freeones.com', '57) www.freshporn.info', '58) www.fuckcuck.com', '59) www.gracefulnudes.com',
         '60) www.gayboystube.com', '61) www.fuq.com', '62) www.hairy.com', '63) www.hindisex.com',
         '64) www.iknowthatgirl.com', '65) www.indianpornovid.com', '66) www.indianpornvideos.com',
         '67) www.ixxx-tube.com', '68) www.ixxx.com', '69) www.ixxx.com.es', '70) www.ixxx.ws', '71) www.jizzhut.com',
         '72) www.labatidora.net', '73) www.leche69.com', '74) www.livjasmin.com', '75) www.locasporfollar.com',
         '76) www.lushstories.com', '77) www.mc-nudes.com', '78) www.milfmovs.com', '79) www.myfreecams.com',
         '80) www.naughty.com', '81) www.penguinvids.com', '82) www.perfectgirls.net', '83) www.perucaseras.com',
         '84) www.pinkworld.com', '85) www.playboy.com', '86) www.playvid.com', '87) www.pornhub.com',
         '88) www.porno.com', '89) www.pornorc.net', '90) www.porntube.com', '91) www.puritanas.com',
         '92) www.redtube.com', '93) www.rk.com', '94) www.roundandbrown.com', '95) www.serviporno.com',
         '96) www.sexocean.com', '97) www.teenpornxxx.net', '98) www.thefreecamsecret.com', '99) www.tnaflix.com',
         '100) www.truthordarepics.com', '101) www.tube8.com', '102) www.tubegalore.com',
         '103) www.videosdemadurasx.com', '104) www.watchmygf.com', '105) www.x-ho.com', '106) www.xixx.com',
         '107) www.xnxx.com', '108) www.xtube.com', '109) www.xvideosnacional.com', '110) www.xxx.com',
         '111) www.youjizz.com', '112) www.youporn.com', '113) xhamster.com', '114) xhot.sextgem.com', '115) xxx.com',
         '116) www.jeux-flash-sexy.com', '117) www.purebbwtube.com', '118) www.babes.com',
         '119) www.fotomujeres.pibones.com', '120) www.rubber-kingdom.com', '121) savitabhabhi.mobi',
         '122) pinkvisualtgp.com', '123) www.antarvasna.com', '124) www.hot-gifz.com', '125) www.lechecallente.com',
         '126) www.parejasfollando.es', '127) www.flirthookup.com', '128) www.cerdas.com', '129) es.chaturbate.com',
         '130) www.youngpornvideos.com', '131) www.nudevista.com', '132) 2gayboys.com', '133) pornxxxtubes.com',
         '134) www.ledauphine.com', '135) freex.mobi', '136) www.megavideoporno.org', '137) www.pornochaud.com',
         '138) www.gokabyle.com', '139) bdenjoymore.blogspot.com', '140) www.petardas.com', '141) www.toroporno.com',
         '142) conejox.com', '143) www.sambaporno.com', '144) www.voyeurpipi.com', '145) porn.mangassex.com',
         '146) goulnes.pornoxxxi.net', '147) videos-x.xpornogays.com', '148) www.indienne-sexy.com',
         '149) www.arabebaise.com', '150) www.ohasiatique.com', '151) www.porn.com', '152) xxxonxxx.com',
         '153) www.sexxxdoll.com', '154) www.xxxvideosex.org', '155) www.gonzoxxxmovies.com', '156) www.keezmovies.com',
         '157) www.xxx.xxx', '158) www.poringa.net', '159) www.videosxxxputas.xxx', '160) lisaannlovers11.tumblr.com',
         '161) h33t.to', '162) www.premiercastingporno.com', '163) www.marocainenue.com', '164) fr.perfectgirls.net',
         '165) www.jeffdunhamfuckdoll.com', '166) www.pornmotion.com', '167) www.gorgeousladies.com',
         '168) www.fille-nue-video.com', '169) www.teensnow.com', '170) www.theofficiallouisejenson.com',
         '171) bangbros.com', '172) yourather.com', '173) bootlus.com', '174) www.conejox.com',
         '175) www.toonztube.com', '176) www.top-chatroulette.com', '177) videosfilleschaudes.com',
         '178) www.fillechaude.com', '179) femmesmuresx.net', '180) www.liberteenage.com', '181) coffetube.com',
         '182) awesomeellalove.tumblr.com', '183) www.xnxxgifs.com', '184) www.gaygautemela.com',
         '185) saoulbafjojo.com', '186) pornofemmeblack.com', '187) sexonapria.org', '188) www.beurettehot.net',
         '189) woodstockreborn.tumblr.com', '190) www.freesex.com', '191) www.peliculaspornogratisxxx.com',
         '192) www.porno-algerienne.com', '194) belles-femmes-arabes.blogspot.com', '195) www.lesbiennesxxx.com',
         '196) des-filles-sexy.com', '197) www.videos-porno-chaudes.com', '198) www.xgouines.com',
         '199) www.couleurivoire.com', '200) 3animalsextube.com', '201) moncotube.net',
         '202) mouparkstreet.blogspot.com', '203) sexocean.com', '204) www.sexcoachapp.com',
         '205) www.femdomecpire.com', '206) babosas.co', '207) www.guide-asie.com', '208) www.beauxcul.com',
         '209) www.maghrebinnes.xl.cx', '210) axnxxx.org', '211) xnxx-free.net', '212) xnxx.vc',
         '213) es.bravotube.net', '214) www.femmesporno.com', '215) www.tubeduporno.com',
         '216) videos-sexe.1touffe.com', '217) video-porno.videurdecouilles.com', '218) www.rubias19.com',
         '219) xxi.onxxille.com', '220) www.asiatique-femme.com', '221) www.masalopeblack.com',
         '222) beautyandthebeard1.tumblr.com', '223) beautiful-nude-teens-exposed.tumblr.com',
         '224) www.porno-marocaine.com', '225) www.69rueporno.com', '226) fuckmycheatingslutwife.tumblr.com',
         '227) www.arabe-sexy.com', '228) www.film-porno-black.com', '229) www.sexe-evbony.com',
         '230) www.gratishentai.net', '231) cochonnevideosx.com', '232) chaudassedusexe.com', '233) videosanalesx.com',
         '234) www.pornotantique.com', '235) dorceltv.xn.pl', '236) video-sex.femmesx.net', '237) www.boutique-sexy.ch',
         '238) www.salope-marocaine.com', '239) www.pornocolumbia.co', '240) www.jeunette18.com',
         '241) www.sexe2asiatique.com', '242) www.redtuve.com', '243) www.les-groses.net', '244) www.nexxx.com',
         '245) freesex.com', '246) www.videospornonacional.com', '247) www.xxxkinky.com', '248) www.yasminramos.com',
         '249) www.tukif.com', '250) porno-wife.com', '251) www.film-xxx-black.com', '252) www.sex.com',
         '253) every-seconds.tumblr.com', '254) adultwork.com', '255) hairy.com', '256) www.tendance-lesbienne.com',
         '257) jpangel101.tumblr.com', '258) 18teensexposed.tumblr.com', '259) girthyencounters.tumblr.com',
         '260) cuckinohio.tumblr.com', '261) dildosatisfaction.tumblr.com', '262) stretchedpussy.tumblr.com',
         '263) mindslostinlust.tumblr.com', '264) whoresmilfsdegraded.tumblr.com',
         '265) bigdickswillingchicks.tumblr.com', '266) www.indiansexstories.net', '267) beeg.com', '268) www.eros.com',
         '269) www.brazzersnetwork.com', '270) sextubelinks.com', '271) xxxbunker.com', '272) 7dog.com',
         '273) vivthomas.com', '274) www.porn00.org', '275) www.teensnowxvideos.com', '276) www.x-art.com',
         '277) chaturbate.com', '278) pinkworld.com', '279) www.pandamovies.com', '280) www.muyzorras.com',
         '281) videos-porno.x18xxx.com', '282) uplust.com', '283) www.shemales.com', '284) www.bigboobsalert.com',
         '285) www.culx.org', '286) www.gay43.com', '287) blogfalconstudios.com', '288) store.falconstudios.com',
         '289) www.premium.gays.com', '290) www.omegaporno.com', '291) www.specialgays.com', '292) www.gggay.com',
         '293) www.nautilix.com', '294) www.ovideox.com', '295) www.aztecaporno.com', '296) hard.pornoxxl.org',
         '297) xxl.sexgratuits.com', '298) www.pornosfilms.com', '299) www.herbalviagraworld.com',
         '300) www.primecurves.com', '301) xbabe.com', '302) webpnudes.com', '303) www.hornybook.com',
         '304) www.pinsex.com', '305) smutty.com', '306) www.dreammovies.com', '307) pornhubfillesalope.com',
         '308) girlygifporn.com', '309) arabicdancevideo.blogspot.com', '310) kellydivine.co',
         '311) www.tubepornstars.com', '312) vintagehairy.net', '313) lookatvintage.com', '314) www.pornorama.com',
         '315) www.ass4all.com', '316) www.cindymovies.com', '317) www.jizzle.com', '318) www.onlygirlvideos.com',
         '319) roflpot.com', '320) www.spankwire.com', '321) www.arabesexy.com', '322) megamovie.us',
         '323) www.nakedboobs.net', '324) www.teencamvids.org', '325) nudeboobshotpics.com', '326) live.sugarbbw.com',
         '327) sexbotbonnasse.com', '328) popurls.com', '329) salope.1japonsex.com',
         '330) www.nudematurewomenphotos.com', '331) www.eroticbeauties.net', '332) milfs30.com',
         '333) freshmatureporn.com', '334) matureshine.com', '335) wetmaturewhores.com', '336) matures-photos.com',
         '337) www.mature-galleries.org', '338) owsmut.com', '339) maturestation.com', '340) webcam.com',
         '341) maturelle.com', '342) womenmaturepics.com',
         '343) www.all-free-nude-old-granny-mature-women-xxx-porn-pics.com', '344) maturepornhub.com',
         '345) www.nudeold.com', '346) www.uniquesexymoms.com', '347) www.nude-oldies.com', '348) www.riomature.com',
         '349) hot-naked-milfs.com', '350) stiflersmoms.com', '351) www.multimature.com', '352) www.oldhotmoms.com',
         '353) matureoracle.com', '354) hungrymatures.com', '355) milfous.com', '356) www.watchersweb.com',
         '357) www.eromatures.net', '358) mom50.com', '359) grannyxxx.co.uk', '360) maturesinstockings.com',
         '361) imaturewomen.com', '362) wetmaturewomen.com', '363) www.matureandyoung.com', '364) www.momshere.com',
         '365) riomoms.com', '366) www.kissmaturesgo.com', '367) bitefaim.com', '368) milfionaire.com',
         '369) sexymaturethumbs.com', '370) www.maturosexy.com', '371) 6mature9.com', '372) www.hotnakedoldies.com',
         '373) golden-moms.com', '374) www.madmamas.com', '375) www.womanolder.com', '376) www.matureland.net',
         '377) motherstits.com', '378) unshavenpussies.net', '379) www.pornmaturepics.com', '380) 105matures.com',
         '381) www.momstaboo.com', '382) broslingerie.com', '383) www.elderly-women.com', '384) upskirttop.net',
         '385) www.bushypussies.net', '386) amateurmaturewives.com', '387) www.universeold.com',
         '388) www.unshavengirls.net', '389) oldernastybitches.com', '390) maturewant.com', '391) www.juliepost.com',
         '392) mulligansmilfs.com', '393) bestmaturewomen.com', '394) riomature.com', '395) www.mature-orgasm.com',
         '396) inlovewithboobs.com', '397) www.riotits.net', '398) www.nakedbustytits.com', '399) www.ass-butt.com',
         '400) www.matureladiespics.com', '401) www.pornmaturewomen.com', '402) www.nudemomphotos.com',
         '403) www.secinsurance.com', '404) www.bigfreemature.com', '405) mature-women-tube.net',
         '406) www.hotnudematures.com', '407) oldsexybabes.net', '408) www.matureasspics.com', '409) mature30plus.com',
         '410) matureamour.com', '411) themomsfucking.net', '412) boobymilf.com', '413) fantasticwomans.com',
         '414) xxxmaturepost.com', '415) www.alloldpics.com', '416) lenawethole.com', '417) www.mature.nl',
         '418) www.wifezilla.com', '419) www.chubbygalls.com', '420) www.nudematurespics.com', '421) www.matureal.com',
         '422) www.thexmilf.com', '423) www.cocomilfs.com', '424) www.zmilfs.com', '425) wild-matures.com',
         '426) horny-matures.net', '427) grandmabesttube.com', '428) www.bestmilftube.com', '429) needmilf.com',
         '430) girlmature.com', '431) www.bestmatureclips.com', '432) www.lustfuloldies.com', '433) www.riomoms.com',
         '434) www.maturehotsex.com', '435) bettermilfs.com', '436) www.milfionaire.com', '437) www.oldercherry.com',
         '438) www.sexymilfpussy.com', '439) www.maturepornpics.com', '440) action36.com', '441) www.dianapost.com',
         '442) babesclub.net', '443) lovely-mature.net', '444) bestmaturesthumb.com', '445) myfreemoms.com',
         '446) milfatwork.net', '447) milfgals.net', '448) olderwomenarchive.com', '449) www.milfmomspics.com',
         '450) www.pornovideo.italy.com', '451) stiflersmilfs.com', '452) maturenags.com', '453) maturenakedsluts.com',
         '454) tgpmaturewoman.com', '455) www.idealwifes.com', '456) maturewitch.com', '457) www.hqmaturemovs.com',
         '458) mature-women-tube.org', '459) www.olderwomentaboo.com', '460) www.chocomilf.com',
         '461) www.milfparanoia.com', '462) www.momsnightjob.com', '463) www.matureintros.com', '464) booloo.com',
         '465) www.bigbuttmature.com', '466) www.maturetube.com', '467) www.mature30-45.com', '468) www.maturecool.com',
         '469) www.mamitatube.com', '470) www.freematurevideo.net', '471) silkymoms.com', '472) www.momsclan.com',
         '473) www.bravomamas.com', '474) www.sharedxpics.com', '475) www.fuckmaturewhore.com', '476) maturedummy.com',
         '477) hotfreemilfs.com', '478) www.el-ladies.com', '479) www.xxxmomclips.com', '480) www.idealmilf.com',
         '481) www.alexmatures.com', '482) www.kingsizebreasts.com', '483) www.matureladies.com',
         '484) www.bigtitsnaked.com', '485) www.xebonygirls.com', '486) www.numaturewomen.com',
         '487) www.womeninyears.com', '488) www.maturehere.com', '489) www.milfpicshere.com',
         '490) www.maturepicsarchive.com', '491) viewmature.com', '492) www.womenmaturepics.com', '493) momspics.net',
         '494) www.cleomture.com', '495) milf-fucking.net', '496) www.maturecherry.net', '497) immoralmatures.com',
         '498) www.pretty-matures.com', '499) matureclithunter.com', '500) ilovematurewomen.tumblr.com',
         '501) www.nudematurepussy.com', '502) www.nudemomandboy.com', '503) www.mygranny.pics',
         '504) www.eroticteens.pw', '505) www.pussy-mature.com', '506) www.fatsexygirls.net',
         '507) www.40somethingmag.com', '508) www.tgpmaturewoman.com', '509) www.amazingmaturesluts.com',
         '510) www.milftubevids.com', '511) www.myhdshop.com', '512) matureholes.net', '513) vipoldies.net',
         '514) juicy-matures.com', '515) hotelmatures.com', '516) www.gaytube.com', '517) hardsexyyoupornhub.com',
         '518) lewd-babes.com', '519) xxx.adulttube.com', '520) maturesexy.us', '521) www.galsarchive.com',
         '522) maturegirl.us', '523) sexpics.xxx', '524) www.mature-for-you.com', '525) www.mulligansmilfs.com',
         '526) www.gracefulmilf.com', '527) www.momsforporn.com', '528) www.sexyhotmilf.com', '529) www.azgals.com',
         '530) www.thematureladies.com', '531) ahmilf.com', '532) www.cheatwife.com', '533) www.picsboob.com',
         '534) www.agedmamas.com', '535) www.bigtitsmilf.com', '535) www.mturemomsporn.com',
         '536) www.older-beauty.com', '537) www.empflix.com', '538) www.numoms.com', '539) www.ladymom.com',
         '540) www.ladymom.com', '541) www.petiteporn.pw', '542) www.grannyhairy.net', '543) gramateurs.com',
         '544) www.sexy-olders.com', '545) fresh-galleries.com', '546) www.nudematuremix.com', '547) alansanal.com',
         '548) www.mature-library.com', '549) www.filthymamas.com', '550) mature-beach.com',
         '551) www.sexualolders.com', '552) www.horny-olders.com', '553) www.olderkiss.com',
         '554) www.wethairywats.com', '555) www.erotic-olders.com', '556) www.maturemompics.com',
         '557) www.maturedally.net', '558) www.place21.com', '559) www.teenhana.com', '560) www.classic-moms.com',
         '561) www.grandmammapics.com', '562) www.xmilfpics.com', '563) www.hotchicks.sexy',
         '564) www.ebonyfantasies.com', '565) www.milfbank.com', '566) www.freematurepornpics.com',
         '567) www.agedcunts.net', '568) www.milfsection.met', '569) myexmilf.com', '570) bestmilfsporn.com',
         '571) www.everydaycams.com', '572) www.adultreviews.com', '573) icematures.com', '574) mature4.net',
         '575) milfera.com', '576) www.milfjam.com', '577) www.bbwpornpics.com', '578) www.pornxxx.com',
         '579) www.milfkiss.com', '580) www.chubbygirlpics.com', '581) excitingmatures.com',
         '582) www.hairymaturegirls.com', '583) www.pamelapost.com', '584) www.7feel.net', '585) www.tubefellas.com',
         '586) www.sexymaturethumbs.com', '587) www.sexybuttpics.com', '588) www.sexyhotmilfs.com',
         '589) www.secretarypics.com', '590) www.naked-moms.com', '591) www.momhandjob.com',
         '592) www.sexymaturethumbs.com', '593) www.pornsticky.com', '594) www.hairymilfpics.com',
         '595) www.maturebrotherthumbs.com', '596) www.hotmomsporn.com', '597) nudematuremix.com',
         '598) www.30plusgirls.com', '599) www.wifesbank.com', '600) www.milfsarea.com', '601) www.pornoriver.net',
         '602) www.milfsbeach.com', '603) www.matureguide.com', '604) www.dailyolders.com', '605) www.askyourmommy.com',
         '606) www.free-porn-pics.net', '607) maturedolls.net', '608) juicygranny.com', '609) www.maturepornhere.com',
         '610) www.nakedoldbabes.com', '611) www.stripping-moms.com', '612) sexymaturepussies.com',
         '613) www.owerotica.com', '614) www.old-vulva.com', '615) www.oldmomstgp.com', '616) www.posing-matures.com',
         '617) www.momsecstasy.com', '618) www.gracefulmom.com', '619) www.wetmaturepics.com', '620) wifenaked.net',
         '621) www.maturexxxclipz.com', '622) matureplace.com', '623) www.riomilf.com', '624) www.fresholders.com',
         '625) www.hqoldies.com', '626) bigtitsfree.net', '627) www.amateur-libertins.net',
         '628) www.maturepornqueens.net', '629) amaclips.com', '630) eroticplace.net', '631) www.myonlyhd.com',
         '632) amapics.net', '633) www.30yomilf.com', '634) fuckdc.com', '635) www.mommyxxxmovies.com',
         '636) www.teenpussy.pw', '637) www.imomsex.com', '638) www.matureandgranny.com', '639) milffreepictures.com',
         '640) www.xxxmaturepost.com', '641) uniquesexymoms.com', '642) fuckmaturewhore.com', '643) www.gentlemoms.com',
         '644) www.deviantclip.com', '645) www.oldsweet.com', '646) www.grannypornpics.net',
         '647) www.lewdmistress.com', '648) www.worldxxxphotos.com', '649) www.sweetmaturepics.com',
         '650) www.oldpoon.com', '651) sexymaturepics.com', '652) www.goodgrannypics.com', '653) www.dagay.com',
         '654) www.randyhags.com', '655) www.thegranny.net', '656) www.maturemomsex.com', '657) maturesort.com',
         '658) www.immodestmoms.com', '659) www.immaturewomen.com', '660) www.bigboty4free.com', '661) tiny-cams.com',
         '662) oldwomanface.com', '663) www.home-madness.com', '664) www.posingwomen.com',
         '665) www.maturesensations.com', '666) www.filthyoldies.com', '667) matureclits.net', '668) momsinporn.net',
         '669) maturebabesporno.com', '670) matureinlove.net', '671) bigtitsporn.me', '672) www.xxxolders.com',
         '673) www.freemilfsite.com', '674) sex.pornoxxl.org', '675) queenofmature.com', '676) www.hotmomspics.com',
         '677) www.freemilfpornpics.com', '678) www.ashleyrnadison.com', '679) www.bizzzporno.com',
         '680) www.sexy-links.net', '681) www.hotsexyteensphotos.com', '682) teemns-pic.com',
         '683) video-porno.1lecheuse.com', '684) www.mrskin.com', '685) www.gobeurettes.com',
         '686) actuallyattractiveamateurs.tumblr.com', '687) www.sexynakedamateurgirls.com',
         '688) nudedares.tumblr.com', '689) amateur-sexys.tumblr.com', '690) hothomemadepix.tumblr.com',
         '691) hotamateurclip.com', '692) voyeursport.com', '693) www.upskirt.com', '694) www.fakku.net',
         '695) pornmirror.com', '696) youjizz.ws', '697) insext.net', '698) pahubad.com', '699) www.xtube.nom.co',
         '700) boytikol.com', '701) www.beeg.co', '702) khu18.biz', '703) www.gonzo.com', '704) www.esseporn.com',
         '705) www.myfreepornvideos.net', '706) www.freeones.ch', '707) efukt.com', '708) newsfilter.org',
         '709) xxxvideo.com', '710) video-one.com', '711) www.pornstarhangout.com', '712) www.breeolson.com',
         '713) porn720.com', '714) www.collegehumor.com', '715) www.barstoolsports.com', '716) hollywoodjizz.com',
         '717) shitbrix.com', '718) xxxsummer.net', '719) porny.com', '720) video.freex.mobl', '721) dixvi.com',
         '722) pornnakedgirls.com', '723) realitypassplus.com', '724) www.digitalplayground.com', '725) 9gag.tv',
         '726) www.kickass.com', '727) es.xhamster.com', '728) sex3.com', '729) www.bravioteens.com',
         '730) www.katestube.com', '731) yourlust.com', '732) wixvi.com', '733) www.porntubevidz.com',
         '734) www.3movs.com', '735) www.buzzwok.com', '736) largepontube.com', '737) kickass.co', '738) godao.com',
         '739) www.hardsextube.com', '740) www.ah-me.com', '741) www.nuvid.com', '742) www.10pointz.com',
         '743) jrunk.tumblr.com', '744) www.pornerbros.com', '745) www.porndig.com', '746) www.bigtinz.com',
         '747) www.8nsex.com', '748) www.imagefap.com', '749) adultfriendfinder.com', '750) www.pornodoido.com',
         '751) www.hdrolet.com', '752) xpornking.com', '753) www.pornokutusu.com', '754) pornzz.com',
         '755) www.pornoforo.com', '756) milfpornet.com', '757) www.kink.com', '758) squirtingmastery.com',
         '759) www.thehotpics.com', '760) www.pof.com', '761) eatyouout.tumblr.com', '762) playboy.com',
         '763) milfsaffair.com', '764) www.indiangilma.com', '765) www.private.com', '766) fuck-milf.com',
         '767) foto-erotica.es', '768) www.daultpornvideox.com', '769) es.bongacams.com', '770) ww.lastsexe.com',
         '771) www.pinksofa.com', '772) www.pinkcupid.com', '773) www.onlyporngif.com', '774) sexyono.com',
         '775) www.shitbrix.com', '776) motherless.com', '777) thehotpics.com', '778) www.joncjg.blogspot.in',
         '779) fr-nostradamus.com', '780) masturbationaddicton.net', '781) japanesexxxtube.com',
         '782) www.kilopics.com', '783) www.find-best-lingerie.com', '784) www.dustyporn.com', '785) cleoteener.com',
         '786) teen18ass.com', '787) www.eternaldesire.com', '788) www.sexyteensphotos.com', '789) teenpornjoy.com',
         '790) www.bubblebuttpics.com', '791) allofteens.com', '792) www.tinysolo.com', '793) www.mynakedteens.com',
         '794) youngmint.com', '795) www.yourlustgirlfriends.com', '796) www.youngxxxpics.com',
         '797) www.pinkteenpics.com', '798) www.clit7.com', '799) www.find-best-videos.com',
         '800) www.freekiloclips.com', '801) www.nudeartstars.com', '802) www.freeporndr.com',
         '803) www.superdiosas.com', '804) www.disco-girls.com', '805) www.lewd-girls.com', '806) mega-teen.com',
         '807) www.heganporn.com', '808) www.pornstarnirvna.com', '809) www.llveleak.com', '810) rude.com',
         '811) www.anatarvasnavideos.com', '812) tour.fuckmyindiangf.com', '813) desindian.sextgem.com',
         '814) www.iscindia.org', '815) www.tubegogo.com', '816) in.spankbang.com', '817) www.yehfun.com',
         '818) www.indiankahani.com', '819) www.pornmdk.com', '820) www.tubestack.com', '821) www.desikahani.net',
         '822) xesi.mobi', '823) www.desitales.com', '824) www.allindiansex.com', '825) www.tubexclips.com',
         '826) boyddl.com', '827) www.comicmasala.com', '828) www.slutload.com', '829) www.befuck.com',
         '830) www.porn20.org', '831) allindiansexstories.com', '832) cinedunia.com', '833) www.bollywood-sex.net',
         '834) www.funjadu.com', '835) iloveindiansex.com', '836) www.hyat.mobi', '837) m.chudaimaza.com',
         '838) www.adultphonechatlines.co.uk', '839) fsiblog.com', '840) www.fucking8.com', '841) www.cloaktube.com',
         '842) indianhotjokes.blogspot.in', '843) wegret.com', '844) www.indiansgoanal.org', '845) www.desipapa.com',
         '846) alizjokes.blogspot.in', '847) jlobster.com', '848) www.desikamasutra.com', '849) www.myhotsite.net',
         '850) hindi-sex.net', '851) www.bullporn.com', '852) oigh.info', '853) jizzporntube.com',
         '854) nonvegjokes.com', '855) www.eeltube.com', '856) www.haporntube.com', '857) hindiold.com']
minecraft = ['As seen on TV!', 'The End?', 'Should not be played while driving.', '1% sugar!', 'Ph1lza had a good run!',
             'Awesome!', '100% pure!', 'May contain nuts!', 'All is full of love!', 'More polygons!',
             'Limited edition!', 'Flashing letters!', 'Made by Notch!', "It's here!", 'Put that cookie down!',
             'Best in class!', "It's finished!", 'Kind of dragon free!', 'Call you Mom!', 'Excitement!',
             'More than 500 sold!', 'One of a kind!', 'Heaps of hits on YouTube!', 'Indev!', 'Spiders everywhere!',
             'Check it out!', 'Holy cow, man!', "It's a game!", 'Made in Sweden!', 'Uses LWJGL!',
             'Reticulating splines!', 'Minecraft!', 'Yaaay!', 'Singleplayer!', 'Keyboard compatible!', 'Undocumented!',
             'Ingots!', 'Exploding creepers!', "That's no moon!", 'L33t!', 'Create!', 'Survive!', 'Dungeon!',
             'Exclusive!', "The bee's knees!", 'Down with O.P.P.!', 'Closed source!', 'Classy!', 'Wow!',
             'Not on steam!', 'Oh man!', 'Awesome community!', 'Pixels!', 'Teetsuuuuoooo!', 'Kaaneeeedaaaa!',
             'Now with difficulty!', 'Enhanced!', '90% bug free!', 'Pretty!', '12 herbs and spices!', 'Fat free!',
             'Absolutely no memes!', 'Free dental!', 'Ask your doctor!', 'Minors welcome!', 'Cloud computing!',
             'Legal in Finland!', 'Hard to label!', 'Technically good!', 'Bringing home the bacon!', 'Indie!', 'GOTY!',
             "Ceci n'est pas une title screen!", 'Euclidian!', 'Now in 3D!', 'Inspirational!', 'Herregud!',
             'Complex cellular automata!', 'Yes, sir!', 'Played by cowboys!', 'OpenGL 1.2!', 'Thousands of colors!',
             'Try it!', 'Age of Wonders is better!', 'Try the mushroom stew!', 'Sensational!',
             'Hot tamale, hot hot tamale!', 'Play him off, keyboard cat!', 'Guaranteed!', 'Macroscopic!',
             'Bring it on!', 'Random splash!', 'Call your mother!', 'Monster infighting!', 'Loved by millions!',
             'Ultimate edition!', 'Freaky!', "You've got a brand new key!", 'Water proof!', 'Uninflammable!',
             'Whoa, dude!', 'All inclusive!', 'Tell your friends!', 'NP is not in P!', 'Notch <3 ez!', 'Music by C418!',
             'Livestreamed!', 'Haunted!', 'Polynomial!', 'Terrestrial!', 'Full of stars!', 'Scientific!',
             'Cooler than Spock!', 'Collaborate and listen!', 'Never dig down!', 'Take frequent breaks!', 'Not linear!',
             'Han shot first!', 'Nice to meet you!', 'Buckets of lava!', 'Ride the pig!', 'Larger than Earth!',
             'sqrt(-1) love you!', 'Phobos anomaly!', 'Punching wood!', 'Falling off cliffs!', '150% hyperbole!',
             'Synecdoche!', "Let's dance!", 'Seecret Friday update!', 'Reference implementation!',
             'Lewd with two dudes with food!', 'Kiss the sky!', '20 GOTO 10!', 'Verlet intregration!', 'Peter Griffin!',
             'Do not distribute!', 'Cogito ergo sum!', '[[]] lines of code!', 'A skeleton popped out!',
             'The Work of Notch!', 'The sum of its parts!', 'BTAF used to be good!', 'I miss ADOM!', 'umop-apisdn!',
             'OICU812!', 'Bring me Ray Cokes!', 'Finger-licking!', 'Thematic!', 'Pneumatic!', 'Sublime!', 'Octagonal!',
             'Une baguette!', 'Gargamel plays it!', 'Rita is the new top dog!', 'SWM forever!', 'Representing Edsbyn!',
             'Matt Damon!', 'Supercalifragilisticexpialidocious!', "Consummate V's!", 'Cow Tools!', 'Double buffered!',
             'Fan fiction!', 'Jason! Jason! Jason!', 'Hotter than the sun!', 'Internet enabled!', 'Autonomous!',
             'Engage!', 'Fantasy!', 'DRR! DRR! DRR!', 'Kick it root down!', 'Regional resources!', 'Woo, facepunch!',
             'Woo, somethingawful!', 'Woo, /v/!', 'Woo, tigsource!', 'Woo, minecraftforum!', 'Woo, worldofminecraft!',
             'Woo, reddit!', 'Woo, 2pp!', 'Google anlyticsed!', 'Now supports åäö!', 'Give us Gordon!',
             'Tip your waiter!', 'Very fun!', '12345 is a bad password!', 'Vote for net neutrality!',
             'Lives in a pineapple under the sea!', 'MAP11 has two names!', 'Omnipotent!', 'Gasp!', '...!',
             'Bees, bees, bees, bees!', 'Jag känner en bot! (I feel a cure!)',
             "This text is hard to read if you play the game at the default resolution, but at 1080p it's fine!",
             'Haha, LOL!', 'Hampsterdance!', 'Switches and ores!', 'Menger sponge!', 'idspispopd!',
             'Eple (original edit)!', 'So fresh, so clean!', 'Slow acting portals!', 'Try the Nether!',
             "Don't look directly at the bugs!", 'Oh, ok, Pigmen!', 'Finally with ladders!', 'Scary!',
             'Play Minecraft, Watch Topgear, Get Pig!', 'Twittered about!', 'Jump up, jump up, and get down!',
             'Joel is neat!', 'A riddle, wrapped in a mystery!', 'Huge tracts of land!', 'Welcome to your Doom!',
             'Stay a while, stay forever!', 'Stay a while and listen!', 'Treatment for your rash!', '"Autological" is!',
             'Information wants to be free!', '"Almost never" is an interesting concept!', 'Lots of truthiness!',
             'The creeper is a spy!', 'Turing complete!', "It's groundbreaking!", "Let our battle's begin!",
             'The sky is the limit!', 'Jeb has amazing hair!', 'Casual gaming!', 'Undefeated!', 'Kinda like Lemmings!',
             'Follow the train, CJ!', 'Leveraging synergy!',
             "This message will never appear on the splash screen, isn't that weird? (This message will not actually appear on the splash screen of Minecraft. It can only be seen in the Minecraft splash text files.)",
             'DungeonQuest is unfair!', '110813!', '90210!', 'Check out the far lands!', 'Tyrion would love it!',
             'Also try VVVVVV!', 'Also try Super Meat Boy!', 'Also try Terraria!', 'Also try Mount And Blade!',
             'Also try Project Zomboid!', 'Also try World of Goo!', 'Also try Limbo!', 'Also try Pixeljunk Shooter!',
             'Also try Braid!', "That's super!", 'Bread is pain!', 'Read more books!', 'Khaaaaaaaaan!',
             'Less addictive than TV Tropes!', 'More addictive than lemonade!', 'Bigger than a bread box!',
             'Millions of peaches!', 'Fnord!', 'This is my true form!', 'Totally forgot about Dre!',
             "Don't bother with the clones!", 'Pumpkinhead!', 'Hobo humping slobo babe!', 'Made by Jeb!',
             'Has an ending!', 'Finally complete!', 'Feature packed!', 'Boots with the fur!', 'Stop, hammertime!',
             'Testificates!', 'Conventional!', 'Homeomorphic to a 3-sphere!', "Doesn't avoid double negatives!",
             'Place ALL the blocks!', 'Does barrel rolls!', 'Meeting expectations!', 'PC gaming since 1873!',
             'Ghoughpteighbteau tchoghs!', 'Déjà vu!', 'Got your nose!', 'Haley loves Elan!',
             'Afraid of the big, black bat!', "Doesn't use the U-word!", "Child's play!", 'See you next Friday or so!',
             'From the streets of Södermalm!', '150 bpm for 400000 minutes!', 'Technologic!', 'Funk soul brother!',
             'Pumpa kungen!', '日本ハロー！', '한국 안녕하세요!', 'Helo Cymru!', 'Cześć Polska!', '你好中国！', 'Привет Россия!',
             'Γεια σου ελλάδα!', 'My life for Aiur!', 'Lennart lennart = new Lennart();',
             'I see your vocabulary has improved!', 'Who put it there?', "You can't explain that!",
             'If not ok then return end', '§1C§2o§3l§4o§5r§6m§7a§8t§9i§ac', '§kFUNKY LOL', 'Flavor with no seasoning!',
             'Strange, but not a stranger!', 'Tougher than diamonds, rich like cream!', 'Getting ready to show!',
             'Getting ready to know!', 'Getting ready to drop!', 'Getting ready to shock!', 'Getting ready to freak!',
             'Getting ready to speak!', 'It swings, it jives!', 'Cruising streets for gold!',
             'Take an eggbeater and beat it against a skillet!', 'Make me a table, a funky table!',
             'Take the elevator to the mezzanine!', 'Stop being reasonable, this is the Internet!', '/give @a hugs 64',
             'This is good for Realms.', "Any computer is a laptop if you're brave enough!", 'Do it all, everything!',
             'Where there is not light, there can spider!', 'GNU Terry Pratchett', 'More Digital!',
             'Falling with style!', "There's no stopping the Trollmaso", 'Throw yourself at the ground and miss',
             "Rule #1: it's never my fault", 'Replaced molten cheese with blood?',
             'Absolutely fixed relatively broken coordinates', 'Boats FTW', 'Javalicious edition',
             'Should not be played while driving!', "You're going too fast!", "Don't feed chocolate to parrots!",
             'The true meaning of covfefe', 'An illusion! What are you hiding?', "Something's not quite right...",
             'Monster infighting!', 'missingno', "In case it isn't obvious, foxes aren't players.", 'Buzzy Bees!',
             'Minecraft Java Edition presents: Disgusting Bugs', 'Team Mystic!', 'Hamilton!',
             '(Bedrock Edition beta test) Beta!', 'Absolutely no memes!', 'Bedrock Edition Exclusives',
             'SOPA means LOSER in Swedish!', 'Ported Implementation!', '100% more yellow text!', 'Dramatic lighting!',
             'Pocket!', 'Touch compatible!', 'Annoying touch buttons!', 'MCPE!', 'Uses C++!', 'Almost C++14!',
             'OpenGL ES 2.0+!', 'Quite Indie!', '!!!1!', 'V-synched!', '0xffff-1 chunks', "It's alpha!", 'Endless!',
             'Ask your mother!', 'Toilet friendly!', 'Cubism!', 'Bekarton guards the gate!',
             'flowers more important than grass', 'Multithreaded!', 'Haha, LEL',
             'Play Minecraft: PE, Watch Topgear, Get Pig!', 'Also try Monument Valley!', '& Knuckles!', 'BAYKN',
             "You can't explain that!", 'V-synched!', "Befy Timy's scraped!", 'Reina Hispanoamericana!',
             'Plants vs zombies!', 'I dont need me!', 'Rodeo Stars Is a Ridable Buckling!',
             'Kambal Karibal Is Fighting Cheska!', 'Great job!']


async def refuel():
    a = len(intros) + len(phrases) + len(sentences)
    UraniumDeposits = [Arsenal.col_values(2)[1:], Arsenal.col_values(3)[1:], Arsenal.col_values(4)[1:]]
    print('filling the tank')
    for x in UraniumDeposits:
        phrase = ''
        begin = False
        if x == Arsenal.col_values(2)[1:]:
            k = intros
        elif x == Arsenal.col_values(3)[1:]:
            k = sentences
        elif x == Arsenal.col_values(4)[1:]:
            k = phrases
        for i in x:
            for j in range(0, len(i)):
                if i[j] == '"':
                    if not begin:
                        begin = True
                    elif begin:
                        begin = False
                        if phrase not in k:
                            k.append(phrase)
                        phrase = ''
                else:
                    phrase = phrase + i[j]
    print('locked and loaded')
    b = len(intros) + len(phrases) + len(sentences)
    return "Locked and Loaded \nRetrieved: " + str(b - a) + " phrases and sentences from the Google form \n" + ammo()


phraseBlack = []
sentencesBlack = []
minecraftBlack = []
sitesBlack = []

cooldown = 0
loud = False

# defining the functions here only
def Frase():
    while True:
        cancer = phrases[random.randint(0, len(phrases) - 1)]
        if cancer not in phraseBlack:
            phraseBlack.append(cancer)
            return cancer
        elif len(phrases) == len(phraseBlack):
            return "I am all out of ammo chief"


def sentence():
    while True:
        cancer = sentences[random.randint(0, len(sentences) - 1)]
        if cancer not in sentencesBlack:
            sentencesBlack.append(cancer)
            return cancer
        elif len(sentences) == len(sentencesBlack):
            return "I am all out of ammo chief"


def mine():
    while True:
        cancer = minecraft[random.randint(0, len(minecraft) - 1)]
        if cancer not in minecraftBlack:
            minecraftBlack.append(cancer)
            return cancer
        elif len(minecraft) == len(minecraftBlack):
            return "I am all out of ammo chief"


def site():
    while True:
        cancer = sites[random.randint(0, len(sites) - 1)]
        if cancer not in sitesBlack:
            sitesBlack.append(cancer)
            if cancer[0] in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']:
                cancer = cancer.split(')')[1] + ' (Banned in India) '
            return cancer
        elif len(sitesBlack) == len(sitesBlack):
            return "How much porn you will see da, my database is exhasted"


def ammo():
    return ("Porn titles : - " + str(len(phrases) - len(phraseBlack)) + "\nPink Guy lyrics : - " + str(
        len(sentences) - len(sentencesBlack)) + "\nMinecraft yellow text : - " + str(
        len(minecraft) - len(minecraftBlack)) + "\nPorn sites loaded : - " + str(
        len(sites) - len(sitesBlack)))


def clear(a):
    a.clear()
    return "A blacklist was cleared on " + str(datetime.utcnow())


outputs = [["Thee men talk too much i am did tire of translating thy words especially ", "Shakespeare_CUNT"],
           ["Tired of translating I am, talk too much you do ", 'Yoda_CUNT'],
           ["I am tired of translatin' you dudes. I just wanna smoke crack with ", "Valley_CUNT"],
           ['I im su tured ouff truonsleting yuou, zeet talkateev ', 'European_CUNT'],
           ["I be so tired o' translatin' ye, that talkative ", 'Pirates_of_the_CUNT']]
links = ['shakespeare.json', 'pirate.json', 'yoda.json', 'chef.json', 'valspeak.json']

#  API definitions
async def translate(txt, author):
    global cooldown
    response = requests.get('https://api.funtranslations.com/translate/' + links[random.randint(0, len(links) - 1)],
                            params={"text": txt})
    if response.status_code == 200:
        output = response.json()['contents']['translated']
        auth = author.split('#')[0]
    else:
        A = outputs[random.randint(0, len(outputs) - 1)]
        output = A[0] + author.split('#')[0]
        auth = A[1]
        cooldown = 3600
    return output, auth


async def joke():
    url = "https://jokeapi-v2.p.rapidapi.com/joke/Any"
    querystring = {"type": "single, twopart"}
    headers = {
        'x-rapidapi-key': "b2efcc243dmsh9563d2fd99f8086p161761jsn0796dda8a1e7",
        'x-rapidapi-host': "jokeapi-v2.p.rapidapi.com"
    }
    response = requests.request("GET", url, headers=headers, params=querystring)
    if response.json()['type'] == 'single' and response.json()['error'] == False:
        return response.json()['joke']
    elif response.json()['type'] == 'twopart' and response.json()['error'] == False:
        return response.json()['setup'] + '\n' + response.json()['delivery']

async def Nasa(type):
    if type == 'APoD':
        url = "https://api.nasa.gov/planetary/apod"
        querystring = {'api_key': 'YdNyGnuk3Mr5El8cBLCSSOrAJ7ymjtjuRE3OfBUJ'}
        response = requests.request("GET", url, params=querystring)
        return (response.json()['explanation'], response.json()['hdurl'], response.json()['title'])

@client.event
async def on_ready():
    now = datetime.now()
    current_time = now.strftime("%d/%m/%Y %H:%M:%S")  # logs into aternos
    channel = client.get_channel(799957897017688065)
    print(channel)
    print('The bot is logged in as {0.user}'.format(client))
    if loud:
        await channel.send(
            mine() + "\n====================\nLaunch"
                     "Time : " + current_time + "\nCurrent Server Status : I have no fucking clue lol\n====================\n")
        await channel.send("Refueling...")
        await channel.send(await refuel())
    serverStatus.start()  # starts the presence update loop


@client.event
async def on_message(message):
    with open('file.txt', 'rb') as handle:
        counter = pickle.loads(handle.read())
    print(counter)
    if message.author == client.user:
        return
    # commands
    if message.content.startswith('--'):
        now = datetime.now()
        current_time = now.strftime("%d/%m/%Y %H:%M:%S")
        print(str(message.author) + ' said ' + str(message.content) + ' at ' + current_time)
        if message.content.lower() == '--start':
            await message.channel.send("I don't do that anymore :-P\n" + mine())
        elif message.content.lower() == '--status':
            await message.channel.send("I have no idea bro. \nEnjoying porno : " + Frase())
        # clear and refuel _____________________________________________________________________________________
        elif message.content.lower() == '--clear porn':
            await message.channel.send(clear(phraseBlack))
        elif message.content.lower() == '--clear sites':
            await message.channel.send(clear(sitesBlack))
        elif message.content.lower() == '--clear minecraft':
            await message.channel.send(clear(minecraftBlack))
        elif message.content.lower() == '--clear monke':
            await message.channel.send(clear(sentencesBlack))

        elif message.content.lower() == '--refuel':
            await message.channel.send('Refueling ...')
            await message.channel.send(await refuel())
        # _______________________________________________________________________________________________________
        elif message.content.lower() == '--ping':
            await message.channel.send("pong! " + str(client.latency) + " seconds\n" + mine())
        elif message.content.lower() == '--counter':
            await message.channel.send(
                message.author.mention + " For as long as I have been online, you have spoken " + str(
                    counter[message.author]) + " times.")
        elif message.content.lower() == '--athar1':
            author = message.author
            if str(author) == 'AbsolA1#4589':
                await message.channel.send(f"{author.mention}, the "
                                           f" PussyBitch has been detected \n" + sentence())
                await message.channel.send("Ah I miss the good old days, alas I am no longer capable of providing "
                                           "that info. All of you have aternos accounts, check it on your own from "
                                           "your phone. But I will give you a cool porn site I found " + site())
            else:

                await message.channel.send(
                    "No idea bro, all of you have aternos account now check from phone, take this mienecraft yellow "
                    "text instead. " + mine())

        elif message.content.lower() == '--stop':
            await message.channel.send(sentence())

        elif message.content.lower() == '--ammo':
            await message.channel.send(ammo())
        elif message.content.lower() == '--help':
            if str(message.author) == "clodman84#1215":
                embed = discord.Embed(title="Yes, creator I will comply")
            else:
                embed = discord.Embed(title=mine())
            embed.add_field(name="--start",
                            value="Starts the server { used to :-( }",
                            inline=False)
            embed.add_field(name="--status",
                            value="Gets the server status, online/offline { used to :-( }",
                            inline=False)
            embed.add_field(name="--athar1",
                            value="Gets the server info, including DynIP { used to :-( }",
                            inline=False)
            embed.add_field(name="--list",
                            value="Gets the number of players",
                            inline=False)
            embed.add_field(name="--stop",
                            value="Stops the server { used to :-( }",
                            inline=False)
            embed.add_field(name="--crash",
                            value="Shuts down the bot, clodman only { used to :-( }",
                            inline=False)
            embed.add_field(name="--help",
                            value="Displays this message",
                            inline=False)
            embed.add_field(name="--wait",
                            value="Waits in queue for you { used to :-( }", inline=False)
            embed.add_field(name="--porn",
                            value="Names a random porn title", inline=False)
            embed.add_field(name="--monke",
                            value="Gives Pink Guy song lyrics at random, mostly", inline=False)
            embed.add_field(name="--minecraft",
                            value="Gives a random minecraft splash text", inline=False)
            embed.add_field(name="--website",
                            value="Suggests a porn site for you, half of them are cursed", inline=False)
            embed.add_field(name="--ammo",
                            value="Tells how many porn sites and pink guy lyrics are loaded in memory", inline=False)
            embed.add_field(name="--counter",
                            value="Tells you how many times you have spoken since I have been turned on", inline=False)
            embed.add_field(name="--clear monke/porn/sites/minecraft",
                            value="If the bot runs out of ammo, then doing this will clear the memory and the bot "
                                  "will start repeating itself", inline=False)
            embed.add_field(name="--refuel",
                            value="If the bot runs out of ammo, then doing this will fetch new phrases from the "
                                  "google form",
                            inline=False)
            embed.add_field(name="--joke",
                            value="Tells you a moderately funny joke",
                            inline=False)
            await message.channel.send(embed=embed)
        elif message.content.lower() == '--joke':
            await message.channel.send(joke())
        elif message.content.lower() == '--apod':
            APoD = await Nasa('APoD')
            embed = discord.Embed(title=APoD[2], description=APoD[0], colour=0x1ed9c0)
            embed.set_image(url=APoD[1])
            await message.channel.send(embed=embed)
        elif message.content.lower() == '--porn':
            await message.channel.send(Frase())
        elif message.content.lower() == '--monke':
            await message.channel.send(sentence())
        elif message.content.lower() == '--cooldown':
            await message.channel.send(cooldown)
        elif message.content.lower() == '--minecraft':
            await message.channel.send(mine())
        elif message.content.lower() == '--website':
            await message.channel.send(site())
        elif message.content.lower() == '--counter all':
            await message.channel.send(str(counter))
        elif message.content.lower() == '--wait':
            await message.channel.send("Time is an infinite void, aren't we all waiting for something that never "
                                       "comes closer yet feels like it is. Certified Billi Eyelash moment. " + Frase() + ' moment')
    else:
        author = str(message.author)
        if author not in counter.keys():
            counter.setdefault(author, 1)
            with open('file.txt', 'wb') as handle:
                pickle.dump(counter, handle)
        else:
            counter[author] += 1
            with open('file.txt', 'wb') as handle:
                pickle.dump(counter, handle)

        if counter[author] % 20 == 0 and cooldown == 0 and len(message.content) <= 2048:
            Text = await translate(message.content, str(author))
            embed = discord.Embed(description="*" + Text[0] + "*", colour=0x1ed9c0)
            embed.set_footer(text="-" + Text[1])
            await message.channel.send(embed=embed)


@tasks.loop(seconds=5.0)
async def serverStatus():
    global cooldown
    if cooldown > 0:
        cooldown = cooldown - 5
    if str(datetime.now().strftime('%H:%M:%S')) == '1:30:00':
        channel = client.get_channel(799957897017688065)
        APoD = await Nasa('APoD')
        embed = discord.Embed(title=APoD[2], description=APoD[0], colour=0x1ed9c0)
        embed.set_image(APoD[1])
        embed.set_footer('Good Morning Cunts!')
        await channel.send(embed=embed)
    return


client.run("Nzk1OTYwMjQ0MzUzMzY4MTA0.X_Q9vg.gPgPZT4xIY81CQCfPiGYm3NYSPg")
