"""
The ePMV Adaptor Module

The ePMV Adaptor Module
=======================

This module provides the function to start ePMV, the function that handle the molecule loading, and 
the Adaptor base class.

"""

import sys,os
from Pmv.mvCommand import MVCommand
from Pmv.moleculeViewer import MoleculeViewer
from Pmv.moleculeViewer import DeleteGeomsEvent, AddGeomsEvent, EditGeomsEvent
from Pmv.moleculeViewer import DeleteAtomsEvent, EditAtomsEvent
from Pmv.displayCommands import BindGeomToMolecularFragment
from Pmv.trajectoryCommands import PlayTrajectoryCommand

from Pmv.pmvPalettes import AtomElements
from Pmv.pmvPalettes import DavidGoodsell, DavidGoodsellSortedKeys
from Pmv.pmvPalettes import RasmolAmino, RasmolAminoSortedKeys
from Pmv.pmvPalettes import Shapely
from Pmv.pmvPalettes import SecondaryStructureType

from MolKit.protein import ResidueSetSelector,Chain, Protein,Residue
from MolKit.molecule import Atom


from mglutil.util.recentFiles import RecentFiles

import numpy
import numpy.oldnumeric as Numeric #backward compatibility
import math
from ePMV import comput_util as util
from ePMV.install_plugin import Installer
from ePMV.lightGridCommands import addGridCommand
from ePMV.lightGridCommands import readAnyGrid
from ePMV.lightGridCommands import IsocontourCommand
#TODO:
#add computation (trajectory reading,energy,imd,pyrosetta?,amber)
#check if work with server/client mode...

class loadMoleculeInHost(MVCommand):
    """
    Command call everytime a molecule is read in PMV. Here is define whats happen
    in the hostApp when a molecule is add in PMV.ie creating hierarchy, empty 
    parent optional pointCloud object, camera, light, etc...    
    """    
   
    def __init__(self,epmv):
        """
        constructor of the command. 
        
        @type  epmv: epmvAdaptor
        @param epmv: the embeded PMV object which consist in the adaptor, the molecular
        viewer and the helper.
        """    
        MVCommand.__init__(self)
        self.mv=epmv.mv
        self.epmv = epmv
        
    def checkDependencies(self, vf):
        from bhtree import bhtreelib

    def doit(self, mol, **kw):
        """
        actual function of the command. 
        
        @type  mol: MolKit molecule
        @param mol: the molecule loaded in PMV

        @type  kw: dictionary
        @param kw: the dictionary of optional keywords arguments
        """    
#        sys.stderr.write('loadMolecule in host\n')
#        print "..............................."
        chname=['Z','Y','X','W','V','U','T']
        molname=mol.name#mol.replace("'","")
        #setup some variable
        self.mv.molDispl[molname]={}
        for k in ["cpk","bs","ss","loft","arm","spline","surf","cms","meta"]:
            self.mv.molDispl[molname][k]=False
        self.mv.molDispl[molname]["col"] = None        
        if molname not in self.mv.MolSelection.keys() :
            self.mv.MolSelection[molname]={}
        if molname not in self.mv.selections.keys() :       
            self.mv.selections[molname]={}
        if molname not in self.mv.iMolData.keys() :       
            self.mv.iMolData[molname]=[]
        sc = self.epmv._getCurrentScene()
        #mol=os.path.splitext(os.path.basename(mol))[0]
        #sys.stderr.write('%s\n'%molname)
        if self.epmv.duplicatemol : #molecule already loaded,so the name is overwrite by pmv, add _ind
            print self.epmv.duplicatedMols.keys()
            if mol in self.epmv.duplicatedMols.keys() : self.epmv.duplicatedMols[molname]+=1
            else : self.epmv.duplicatedMols[molname]=1
            molname=molname+"_"+str(self.epmv.duplicatedMols[molname])
        molname=molname.replace(".","_")
        #sys.stderr.write('%s\n'%mol)
        print self.mv.Mols.name                                    
        P=mol=self.mv.getMolFromName(molname)
        if mol == None : 
        #    print "WARNING RMN MODEL OR ELSE, THERE IS SERVERAL MODEL IN THE 
        #    FILE\nWE LOAD ONLY LOAD THE 1st\n",self.Mols.name            
            P=mol=self.mv.getMolFromName(molname+"_model1")
            mol.name=molname
        #mol=mol.replace("_","")
        sys.stderr.write('%s\n'%mol)
        #mol.name = mol.name.replace("_","")        
        self.mv.buildBondsByDistance(mol,log=0)
#        self.mv.computeSESAndSASArea(mol,log=0)
#        sys.stderr.write("center")
        center = mol.getCenter()
#        sys.stderr.write(center)
        #if centering is need we will translate to center
        if self.epmv.center_mol :
            matrix = numpy.identity(4,'f')
            matrix[3,:3] = numpy.array(center)*-1
            #print matrix
            vt=util.transformedCoordinatesWithMatrice(mol,matrix.transpose())
            mol.allAtoms.updateCoords(vt,ind=0)
            #mol.allAtoms.setConformation(0)
            center = mol.getCenter()
            #print center
        if self.epmv.host == 'chimera':
            model=self.epmv.helper.readMol(mol.parser.filename)
            mol.ch_model = model
            mol.geomContainer.masterGeom.obj = model
            return
        if self.epmv.useModeller:
            print "ok add a conf"
            #add a conformation for modeller
            mol.allAtoms.addConformation(mol.allAtoms.coords[:])
            iConf = len(mol.allAtoms[0]._coords)-1
            from ePMV.extension.Modeller.pmvAction import pmvAction
            mol.pmvaction=pmvAction(1, 1, 1000,iconf=iConf,pmvModel=mol,
                                    mv=self.epmv)#skip,first,last
        #create an empty/null object as the parent of all geom, and build the 
        #molecule hierarchy as empty for each Chain 
        master=self.epmv._newEmpty(mol.name,location=[0.,0.,0.])#center)
        mol.geomContainer.masterGeom.obj=master
        self.epmv._addObjectToScene(sc,master)
        mol.geomContainer.masterGeom.chains_obj={}
        mol.geomContainer.masterGeom.res_obj={}        
        if self.epmv.doCloud:
            cloud = self.epmv._PointCloudObject(mol.name+"_cloud",
                                            vertices=mol.allAtoms.coords,
                                            parent=master)
        ch_colors = self.mv.colorByChains.palette.lookup(mol.chains)
        for i,ch in enumerate(mol.chains):
            sys.stderr.write(str(i)+"\n")
            #how to fix this problem...?
            if self.epmv.host =='maya':
                if ch.name == " " or ch.name == "" :
                    #this dont work with stride....name of chain dont stay for ss
                    ch.name = chname[i]
            ch_center=[0.,0.,0.]#util.getCenter(ch.residues.atoms.coords)            
            chobj=self.epmv._newEmpty(ch.full_name(),location=ch_center)#,parentCenter=center)            
            mol.geomContainer.masterGeom.chains_obj[ch.name]=self.epmv._getObjectName(chobj)
            self.epmv._addObjectToScene(sc,chobj,parent=master,centerRoot=True)
            parent = chobj
            #make the chain material
            ch.material = self.epmv.helper.addMaterial(ch.full_name()+"_mat",ch_colors[i])
            if self.epmv.doCloud:
                cloud = self.epmv._PointCloudObject(ch.full_name()+"_cloud",
                                                vertices=ch.residues.atoms.coords,
                                                parent=chobj)
            #self.epmv._addObjectToScene(sc,cloud,parent=chobj)
        #if self.useTree == 'perRes' :
        #        for res in ch.residues : 
        #            res_obj = util.makeResHierarchy(res,parent,useIK='+str(self.useIK)+')
        #            mol.geomContainer.masterGeom.res_obj[res.name]=util.getObjectName(res_obj)
        #elif self.useTree == 'perAtom' : 
        #        for res in ch.residues : 
        #            parent = util.makeAtomHierarchy(res,parent,useIK='+str(self.useIK)+')
        #else :
            chobjcpk=self.epmv._newEmpty(ch.full_name()+"_cpk",location=ch_center)            
            mol.geomContainer.masterGeom.chains_obj[ch.name+"_cpk"]=self.epmv._getObjectName(chobjcpk)
            self.epmv._addObjectToScene(sc,chobjcpk,parent=chobj,centerRoot=True)
            chobjballs=self.epmv._newEmpty(ch.full_name()+"_bs",location=ch_center)            
            mol.geomContainer.masterGeom.chains_obj[ch.name+"_balls"]=self.epmv._getObjectName(chobjballs)
            self.epmv._addObjectToScene(sc,chobjballs,parent=chobj,centerRoot=True)
            chobjss=self.epmv._newEmpty(ch.full_name()+"_ss",location=ch_center)            
            mol.geomContainer.masterGeom.chains_obj[ch.name+"_ss"]=self.epmv._getObjectName(chobjss)
            self.epmv._addObjectToScene(sc,chobjss,parent=chobj,centerRoot=True)
#        sys.stderr.write("some computation")
        radius = util.computeRadius(P,center)
#        sys.stderr.write(str(radius))
        focal = 2. * math.atan((radius * 1.03)/100.) * (180.0 / 3.14159265358979323846)
#        sys.stderr.write(str(focal))
        center =center[0],center[1],(center[2]+focal*2.0)
#        print center
        if self.epmv.doCamera :          
            self.epmv._addCameraToScene("cam_"+mol.name,"ortho",focal,center,sc)
        if self.epmv.doLight :
            self.epmv._addLampToScene("lamp_"+mol.name,'Area',(1.,1.,1.),15.,0.8,1.5,False,center,sc)
            self.epmv._addLampToScene("sun_"+mol.name,'Sun',(1.,1.,1.),15.,0.8,1.5,False,center,sc)

    def onAddObjectToViewer(self, obj):
        apply(self.doitWrapper, (obj,))

    def __call__(self, mol, **kw):
        apply(self.doitWrapper, (mol,), kw)
        
class epmvAdaptor:
    """
    The ePMV Adaptor object
    =======================
            The base class for embedding pmv in a hostApplication
            define the hostAppli helper function to apply according Pmv event.
            Each hostApp adaptor herited from this class.
    """
    keywords={"useLog":None,
        "bicyl":{"name":"Split bonds","value":True,"type":"checkbox"},#one or two cylinder to display a bond stick
        "center_mol":{"name":"Center Molecule","value":True,"type":"checkbox"},
        "center_grid":{"name":"Center Grid","value":True,"type":"checkbox"},
        "joins":None,
        "colorProxyObject":None,	
        "only":None,
        "updateSS":None,
        "use_instances":None,
        "duplicatemol":None,
        "useTree":None,#None#'perRes' #or perAtom	
        "useIK":None,		
        "use_progressBar": {"name":"Use progress bar","value":False,"type":"checkbox"},
        "doCloud":{"name":"Render points","value":True,"type":"checkbox"},
        "doCamera":{"name":"PMV camera","value":True,"type":"checkbox"},
        "doLight":{"name":"PMV light","value":True,"type":"checkbox"},
        "useModeller":{"name":"Use Modeller","value":False,"type":"checkbox"},
        "synchro_realtime":{"name":"Synchro realtime","value":True,"type":"checkbox"},
        "synchro_timeline":{"name":"Synchronize data player to timeline",
                            "value":False,"type":"checkbox"},
        "synchro_ratio":[{"name":"steps every","value":1,"type":"inputInt",
                            "mini":0,"maxi":2000},
                         {"name":"frames","value":1,"type":"inputInt",
                         "mini":0,"maxi":2000}],
        "forceFetch":{"name":"Force downloading on Fetch","value":False,"type":"checkbox"}
        }

    def setupMV(self):
        self.mv.addCommand(BindGeomToMolecularFragment(), 'bindGeomToMolecularFragment', None)
        self.mv.browseCommands('trajectoryCommands',commands=['openTrajectory'],log=0,package='Pmv')
        self.mv.addCommand(PlayTrajectoryCommand(),'playTrajectory',None)
        self.mv.addCommand(addGridCommand(),'addGrid',None)
        self.mv.addCommand(readAnyGrid(),'readAny',None)
        self.mv.addCommand(IsocontourCommand(),'isoC',None)
        #define the listener
        if self.host is not None :
            self.mv.registerListener(DeleteGeomsEvent, self.updateGeom)
            self.mv.registerListener(AddGeomsEvent, self.updateGeom)
            self.mv.registerListener(EditGeomsEvent, self.updateGeom)
            self.mv.registerListener(DeleteAtomsEvent, self.updateModel)
            self.mv.addCommand(loadMoleculeInHost(self),'_loadMol',None)            
            self.mv.embedInto(self.host,debug=0)
        #compatibility with PMV
        self.mv.Grid3DReadAny = self.mv.readAny
        #mv.browseCommands('superimposeCommandsNew', package='Pmv', topCommand=0)
        self.mv.userpref['Read molecules as']['value']='conformations'
        
        #recentFiles Folder
        rcFile = self.mv.rcFolder
        if rcFile:
            rcFile += os.sep + 'Pmv' + os.sep + "recent.pkl"
            self.mv.recentFiles = RecentFiles(self.mv, None, filePath=rcFile,index=0)
        else :
            print "no rcFolder??"
        
        #this  create mv.hostapp which handle server/client and log event system
        #NOTE : need to test it in the latest version
#        if not self.useLog : 
#            self.mv.hostApp.driver.useEvent = True
        self.mv.iTraj={}
#        mv.hostApp.driver.bicyl = self.bicyl

    def __init__(self,mv=None,host=None,useLog=False,debug=0,gui=False,**kw):
        """
        Constructor of the adaptor. Register the listener for PMV events and setup
        defaults options. If no molecular viewer are provided, start a fresh pmv 
        session.
        
        @type  mv: MolecularViewer
        @param mv: a previous pmv cession gui-less
        @type  host: string
        @param host: name of the host application
        @type  useLog: boolean
        @param useLog: use Command Log event instead of Geom event (deprecated)
        @type  debug: int
        @param debug: debug mode, print verbose
        """    
        
        self.mv = mv
        self.host = host
#        self.Set(reset=True,useLog=useLog,**kw)
        if self.mv == None :
            self.mv = self.start(debug=debug)
        self.setupMV()
        self.addADTCommands()
        if not hasattr(self.mv,'molDispl') : self.mv.molDispl={}
        if not hasattr(self.mv,'MolSelection') : self.mv.MolSelection={}
        if not hasattr(self.mv,'selections') : self.mv.selections={}
        if not hasattr(self.mv,'iMolData') :self.mv.iMolData={}
        #options with default values
        self.duplicatedMols={}
        self.env = None
        self.inst = None
        self.gui = None
        self.GUI = None
        self.timer = False
        self.mglroot = ""
        self.setupInst()
        self.ResidueSelector = ResidueSetSelector()
        self.ssk=['Heli', 'Shee', 'Coil', 'Turn', 'Stra']
        self.ResidueSelector=ResidueSetSelector()
        self.AtmRadi = {"A":1.54,"M":1.54,"N":"1.54","C":"1.7","CA":"1.7",
                        "O":"1.52","S":"1.85","H":"1.2","P" : "1.04"}
        self.lookupDGFunc = util.lookupDGFunc

        
    def setupInst(self):
        if self.inst is None :
            self.inst=Installer(gui=False)
#        print "mglroot ",self.mglroot
        if not self.mglroot :
            import Pmv
            dirP = Pmv.__path__[0]
            os.chdir(dirP) #pmv
            os.chdir(".."+os.sep) #MGLToolsPckgs
            os.chdir(".."+os.sep) #mgltools
            self.mglroot = os.path.abspath(os.curdir)
#            print "mglrootx ",self.mglroot
        self.inst.mgltoolsDir=self.mglroot
        self.inst.currDir=self.mglroot+os.sep+"MGLToolsPckgs"+os.sep+"ePMV"+os.sep

    def initOption(self):
        """
        Initialise the defaults options for ePMV, e.g. keywords.
        """    
        for key in self.keywords : 
            if self.keywords[key] is not None and key != "synchro_ratio":
                setattr(self,key,self.keywords[key]["value"])
        
        self.useLog = False
        self.joins=False
        self.colorProxyObject=False	
        self.only=False
        self.updateSS = False
        self.use_instances=False
        self.duplicatemol=False
        self.useTree = 'default'#None#'perRes' #or perAtom	
        self.useIK = False			
        self.useModeller = False #do we use modeller
        self._modeller = False #is modeller present
        self.synchro_ratio = [self.keywords["synchro_ratio"][0]["value"],
                            self.keywords["synchro_ratio"][0]["value"]] #every 1 step for every 1 frame 
        self._AF = False
        self._AR = False
        self.synchronize()
 
    def Set(self,reset=False,**kw):
        """
        Set ePmv options provides by the keywords arguments.
        e.g. epmv.Set(bicyl=True)
        
        @type  reset: bool
        @param reset: reset to default values all options
        @type  kw: dic
        @param kw: list of options and their values.
        """    
        if reset :
            self.initOption()
        
        for k in kw :
            if k in self.keywords.keys() :
                if self.keywords[k] is not None and k != "synchro_ratio":
                    setattr(self,k,kw[k])
                    self.keywords[k]["value"] = kw[k]
        
        val = kw.pop( 'joins', None)
        if val is not None:
            self.joins = val
        val = kw.pop( 'colorProxyObject', None)
        if val is not None:
            self.colorProxyObject = val
        val = kw.pop( 'only', None)
        if val is not None:
            self.only = val
        val = kw.pop( 'updateSS', None)
        if val is not None:
            self.updateSS = val
        val = kw.pop( 'use_instances', None)
        if val is not None:
            self.use_instances = val
        val = kw.pop( 'duplicatemol', None)
        if val is not None:
            self.duplicatemol = val
        val = kw.pop( 'useTree', None)
        if val is not None:
            self.useTree = val
        val = kw.pop( 'useIK', None)
        if val is not None:
            self.useIK = val
        val = kw.pop( 'useModeller', None)
        if val is not None:
            self.useModeller = val
        val = kw.pop( 'synchro_ratio', None)
        if val is not None:
            self.synchro_ratio = val
            #should be a an array [1,1]

    def start(self,debug=0):
        """
        Initialise a PMV guiless session. Load specific command to PMV such as
        trajectory, or grid commands which are not automatically load in the 
        guiless session.
        
        @type  debug: int
        @param debug: debug mode, print verbose
        
        @rtype:   MolecularViewer
        @return:  a PMV object session.
        """    
        mv = MoleculeViewer(logMode = 'overwrite', customizer=None, 
                            master=None,title='pmv', withShell= 0,
                            verbose=False, gui = False)

        return mv

    def addADTCommands(self):
        """
        Add to PMV some usefull ADT commands, and setup the conformation player.
        readDLG
        showDLGstates
        """    

        from AutoDockTools.autoanalyzeCommands import ADGetDLG,StatesPlayerWidget,ShowAutoDockStates
#        from AutoDockTools.autoanalyzeCommands import ADShowBindingSite
        self.mv.addCommand(ADGetDLG(),'readDLG',None)
        #self.mv.addCommand(StatesPlayerWidget(),'playerDLG',None)
        self.mv.addCommand(ShowAutoDockStates(),'showDLGstates',None)
        self.mv.userpref['Player GUI']={}
        self.mv.userpref['Player GUI']['value']='Player'
        
    #general util function
    def createMesh(self,name,g,proxyCol=False,parent=None):
        """
        General function to create mesh from DejaVu.Geom.
        
        @type  name: string
        @param name: name of the host application
        @type  g: DejaVu.Geom
        @param g: the DejaVu geometry to convert in hostApp mesh
        @type  proxyCol: boolean
        @param proxyCol: if need special object when host didnt support color by vertex (ie C4D)
        @type  parent: hostApp object
        @param parent: the parent for the hostApp mesh
        """ 
        vertices=None
        faces=None
        if not hasattr(g,"getVertices"):
            #this os probably a extEl then just get vertices and faces
            vertices = g.vertices
            faces = g.faces
        else :
            vertices =g.getVertices()
            faces =  g.getFaces()
        obj = self._createsNmesh(name,vertices,None,faces,
                           proxyCol=proxyCol)
        self._addObjToGeom(obj,g)
        self._addObjectToScene(self._getCurrentScene(),obj[0],parent=parent)

    def getChainParentName(self,selection,mol):
        """
        Return the hostApp object masterParent at the chain level for a 
        given MolKit selection.
        
        @type  selection: MolKit.AtomSet
        @param selection: the current selection
        @type  mol: MolKit.Protein
        @param mol: the selection's parent molecule 
        
        @rtype:   hostApp object
        @return:  the masterparent object at the chain level or None
        """    
        parent=None
        if len(selection) != len(mol.allAtoms) : 
            chain=selection.findParentsOfType(Chain)[0]
            parent = mol.geomContainer.masterGeom.chains_obj[chain.name]
            parent = self._getObject(parent)
        return parent	

    def compareSel(self,currentSel,molSelDic):
        """
        Comapre the currentSel to the selection dictionary, return selname if retrieved.
        
        @type  currentSel: MolKit.AtomSet
        @param currentSel: the current selection
        @type  molSelDic: dictionary
        @param molSelDic: the dictionary of saved selection
        
        @rtype:   string
        @return:  the name of the selection in the dictionary if retrieved.
        """    
        
        for selname in molSelDic.keys():
            if currentSel[-1] == ';' : currentSel=currentSel[0:-1]
            if currentSel == molSelDic[selname][3] : return selname
            if currentSel == molSelDic[selname] : return selname
        return None

    def getMolName(self,val,forupdate=False):
        print "get ",val
        selname=""
        mname=val
        #print self.mv.iMol.keys()       
        if mname in self.mv.selections.keys(): 
            selname=mname
            print str(val),mname,selname
        else : #it is the selecetionname
            for name in self.mv.selections.keys():
                for sname in self.mv.selections[name].keys():
                    if mname == sname :
                        selname = sname
                        mname = name
        print mname
        mol=self.mv.getMolFromName(mname)
#        print mol.name
        if forupdate: 
            return selname,mol#? 
        return mname,mol

    def getSelectionLevel(self,mol,selString):
        #fix...problem if multiple chain...
        #R=mol.chains[0].residues
        if mol == None : sel = ''
        else : sel=mol.name
        selection=selString
        if selection.upper() == 'BACKBONE':              
            sel=mol.name+":::N,CA,C"
        elif selection.upper() == 'SIDECHAIN':              
            sel=mol.name+":::sidechain"
        elif selection.upper() in AtomElements.keys(): sel=mol.name+':::'+selection
        elif selection.upper() in RasmolAmino.keys(): sel=mol.name+'::'+self.ResidueSelector.r_keyD[selection]+':'
        elif selection.lower() in ResidueSetSelector.residueList.keys() : sel=mol.name+'::'+selection+':'
        elif selection.split(':')[0] == mol.name : sel = selection
        elif selection.split(' ')[0].lower() == "chain" : sel = mol.name+':'+selection.split(' ')[1]+'::'
        elif selection == 'picked' and self.gui is not None: 
            #need to get the current object selected in the doc
            #and parse their name to recognize the atom selection...do we define a picking level ? and some phantom object to be picked?                  
            CurrSel=self._getCurrentSelection()
            astr=[]
            for o in CurrSel : 
                #print o.get_name()#,o.get_type()
                astr.append(self.parseObjectName(o))
            sel=self.sortName(astr)
            print "parsed selection ",sel
            #sel=mol.name
        selection = self.mv.select(str(sel),negate=False, only=True, xor=False, 
                                   log=0, intersect=False)
        if not isinstance(selection,Atom) : selection = selection.findType(Atom)
        return sel,selection

    def getSelectionCommand(self,selection,mol):
        """
        From the given currentSel and its parent molecule, return the selection name
        in the selection dictionary.
        
        @type  selection: MolKit.AtomSet
        @param selection: the current selection
        @type  mol: MolKit.Protein
        @param mol: the selection's parent molecule 
        
        @rtype:   string
        @return:  the name of the selection in the dictionary if retrieved.
        """    
        
        parent=None
        if hasattr(self.mv,"selections") :                         
            parent=self.compareSel('+selection+',self.mv.selections[mol.name])
        return parent    


    def updateModel(self,event):
        """
        This is the callback function called everytime
        a PMV command affect the molecule data, ie deleteAtomSet.
        
        @type  event: VFevent
        @param event: the current event, ie DeleteAtomsEvent
        """    
        
        if isinstance(event, DeleteAtomsEvent):
            action='delete'
        print action
        #when atom are deleted we have to redo the current representation and 
        #selection
        atom_set = event.objects
        #mol = atom_set[0].getParentOfType(Protein)
        #need helperFunction to delete Objects
        for i,atms in enumerate(atom_set):
            nameo = "S"+"_"+atms.full_name()
            o=self._getObject(nameo)
            if o is not None :
                print nameo
                self.helper.deleteObject(o)
            #and the ball/stick
            nameo = "B"+"_"+atms.full_name()
            o=self._getObject(nameo)
            if o is not None :
                print nameo
                self.helper.deleteObject(o)
            #and the bonds...and other geom?
            
            
    #the main function, call every time an a geom event is dispatch
    def updateGeom(self,event):
        """
        This the main core of ePMV, this is the callback function called everytime
        a PMV command affect a geometry.
        
        @type  event: VFevent
        @param event: the current event, ie EditGeomsEvent
        """    
        
        if isinstance(event, AddGeomsEvent):
            action='add'
        elif isinstance(event, DeleteGeomsEvent):
            action='delete'
        elif isinstance(event, EditGeomsEvent):
            action='edit'
        else:
            import warnings
            warnings.warn('Bad event %s for epmvAdaptor.updateGeom'%event)
            return
        nodes,options = event.objects
        if event.arg == 'iso' :
            self._isoSurface(nodes,options)
            return
        mol, atms = self.mv.getNodesByMolecule(nodes, Atom)
        #################GEOMS EVENT############################################
        if event.arg == 'lines' and action =='edit' :
            self._editLines(mol,atms)
        elif event.arg == 'cpk' and action =='edit' and not self.useLog :
           self._editCPK(mol,atms,options)
        elif event.arg == 'bs' and action =='edit' and not self.useLog :
            self._editBS(mol,atms,options)
        elif event.arg == 'trace' and action =='edit' and not self.useLog :
            print "displayTrace not supported Yet"
            #displayTrace should use a linear spline extruded like _ribbon command
        elif event.arg[0:4] == 'msms' and action =='edit' and not self.useLog :
			#there is 2 different msms event : compute msms_c and display msms_ds
            if event.arg == "msms_c" : #ok compute
                self._computeMSMS(mol,atms,options)
            elif event.arg == "msms_ds" : #ok display
                self._displayMSMS(mol,atms,options)     
        elif event.arg[:2] == 'SS' and action =='edit' and not self.useLog :
            if event.arg == "SSextrude":
                self._SecondaryStructure(mol,atms,options,extrude=True)
            if event.arg == "SSdisplay":
                self._SecondaryStructure(mol,atms,options)
        #################COLOR EVENT############################################
        elif event.arg[0:5] == "color" : #color Commands
            #in this case liste of geoms correspond to the first options
            #and the type of function is the last options
            self._color(mol,atms,options)

    def delMolDic(self,mname):
        del self.mv.selections[mname]
        del self.mv.iMolData[mname]
        del self.mv.molDispl[mname]
        del self.mv.MolSelection[mname]

    def delGeomMol(self,mol):
        master = mol.geomContainer.masterGeom.obj
        self.helper.deleteChildrens(master)
        for g in mol.geomContainer.geoms:
            if hasattr(g,'obj'):
                del g.obj 
            if hasattr(g,'mesh'):
                del g.mesh

    def _addMolecule(self,molname):
        """
        Initialise a molecule. ie prepare the specific dictionary for this molecule.
        
        @type  molname: str
        @param molname: the molecule name        
        """            
        if molname not in self.mv.molDispl.keys() :
            self.mv.molDispl[molname]={}
            for k in ["cpk","bs","ss","loft","arm","spline","surf","cms","meta"]:
                self.mv.molDispl[molname][k]=False
            self.mv.molDispl[molname]["col"] = None
        if molname not in self.mv.MolSelection.keys() :
            self.mv.MolSelection[molname]={}
        if molname not in self.mv.selections.keys() :       
            self.mv.selections[molname]={}
        if molname not in self.mv.iMolData.keys() :       
            self.mv.iMolData[molname]=[]
        
    def _deleteMolecule(self,mol):
        if mol.name in self.mv.Mols.name :
            #need to first delete the geom and the associates dictionary
            #note the mesh are still in the memory ....
            self.delMolDic(mol.name)
            self.delGeomMol(mol)
            #then delete the mol
            self.mv.deleteMol(mol, log=0)
            #del cam and light

    def _toggleUpdateSphere(self,atms,display,needRedo,i,N,prefix):
        """
        Handle the visibility and the update (pos) of each atom's Sphere geometry.
        i and N arg are used for progress bar purpose.
        
        @type  atms: MolKit.Atom
        @param atms: the atom to handle
        @type  display: boolean
        @param display: visibility option
        @type  needRedo: boolean
        @param needRedo: do we need to update
        @type  i: int
        @param i: the atom indice
        @type  N: int
        @param N: the total number of atoms
        @type  prefix: str
        @param prefix: cpk or ball sphere geometry, ie "S" or "B"
        """            
        #TODO, fix problem with Heteratom that can have the same fullname
        nameo = prefix+"_"+atms.full_name()
        o=self._getObject(nameo)
        if o != None :
            self._toggleDisplay(o,display)
            if needRedo : 
                self._updateSphereObj(o,atms.coords)
                if self.use_progressBar  and (i%20)==0 : 
                    progress = float(i) / N
                    self._progressBar(progress, 'update Spheres')

    def _toggleUpdateStick(self,bds,display,needRedo,i,N,molname):
        """
        Handle the visibility and the update (pos) of each atom's bonds cylinder geometry.
        i and N arg are used for progress bar purpose.
        
        @type  bds: MolKit.Bonds
        @param bds: the bonds to handle
        @type  display: boolean
        @param display: visibility option
        @type  needRedo: boolean
        @param needRedo: do we need to update
        @type  i: int
        @param i: the atom indice
        @type  N: int
        @param N: the total number of atoms
        @type  molname: str
        @param molname: the name of the parent molecule.
        """                    
        atm1=bds.atom1 
        atm2=bds.atom2 
        if not self.bicyl :
            c0=numpy.array(atm1.coords)
            c1=numpy.array(atm2.coords)
            n1=atm1.full_name().split(":")
            name="T_"+atm1.name+str(atm1.number)+"_"+atm2.name+str(atm2.number)
#            name="T_"+atm1.name+str(atm1.number)+"_"+atm2.name+str(atm2.number)
#            name="T_"+molname+"_"+n1[1]+"_"+util.changeR(n1[2])+"_"+n1[3]+"_"+atm2.name
#            name="T_"+atm1.name+str(atm1.number)+"_"+atm2.name+str(atm2.number)   
            o=self._getObject(name)
            if o != None : 
                if needRedo : 
                    self._updateTubeObj(o,c0,c1) 
                self._toggleDisplay(o,display=display)			
        else :        
            c0=numpy.array(atm1.coords)
            c1=numpy.array(atm2.coords)
            vect = c1 - c0
            n1=atm1.full_name().split(":")
            n2=atm2.full_name().split(":")
            name1="T_"+molname+"_"+n1[1]+"_"+util.changeR(n1[2])+"_"+n1[3]+"_"+atm2.name
            name2="T_"+molname+"_"+n2[1]+"_"+util.changeR(n2[2])+"_"+n2[3]+"_"+atm1.name	                            
            o=self._getObject(name1)
            if o != None : 
                if needRedo : 
                    self._updateTubeObj(o,c0,(c0+(vect/2.)))
                self._toggleDisplay(o,display=display)
            o=self._getObject(name2)
            if o != None : 
                if needRedo : 
                    self._updateTubeObj(o,(c0+(vect/2.)),c1) 
                self._toggleDisplay(o,display=display)
        if self.use_progressBar  and (i%20)==0 : 
                progress = float(i) / N
                self._progressBar(progress, 'update sticks')

    def _editCPK(self,mol,atms,opts):
        """
        Callback for displayCPK commands. Create and update the cpk geometries
        
        @type  mol: MolKit.Protein
        @param mol: the molecule affected by the command
        @type atms: MolKit.AtomSet
        @param atms: the atom selection
        @type  opts: list
        @param opts: the list of option used for the command (only, negate, scaleFactor,
        cpkRad, quality, byproperty, propertyName, propertyLevel, redraw)
        """    
        
        sc = self._getCurrentScene()
        display = not opts[1]

        needRedo = opts[8]
#        print "redo",needRedo
        options=self.mv.displayCPK.lastUsedValues["default"]
        if options.has_key("redraw"): needRedo = options["redraw"]
#        print "redo",needRedo
        ##NB do we want to handle multiple mol at once?
        mol = mol[0]
        g = mol.geomContainer.geoms['cpk']
        root = mol.geomContainer.masterGeom.obj
        chobj = mol.geomContainer.masterGeom.chains_obj
        sel = atms[0]
        if not hasattr(g,"obj") and display: 
            name=mol.name+"_cpk"
            mesh=self._createBaseSphere(name=mol.name+"_b_cpk",quality=opts[4],cpkRad=opts[3],
                                        scale=opts[2],parent=root)
            ob=self._instancesAtomsSphere(name,mol.allAtoms,mesh,sc,scale=opts[2],
                                          R=opts[3],Res=opts[4],join=self.joins,
                                          geom=g,pb=self.use_progressBar)
            self._addObjToGeom([ob,mesh],g)
#            for i,o in enumerate(ob):
#                parent=root
#                hierarchy=self._parseObjectName(o)
#                if hierarchy != "" :
#                    if self.useTree == 'perRes' :
#                        parent = self._getObject(mol.geomContainer.masterGeom.res_obj[hierarchy[2]])
#                    elif self.useTree == 'perAtom' :
#                        parent = self._getObject(o.get_name().split("_")[1])
#                    else :
#                        parent = self._getObject(chobj[hierarchy[1]+"_cpk"])
#                self._addObjectToScene(sc,o,parent=parent)
#                #self._toggleDisplay(o,False)
#                if self.use_progressBar :
#                    progress = float(i) / len(ob)
#                    self._progressBar(progress, 'add CPK to scene')
        #elif hasattr(g,"obj")  and needRedo :
        #    self._updateSphereObjs(g)
        if hasattr(g,"obj"):
            self._updateSphereMesh(g,quality=opts[4],cpkRad=opts[3],scale=opts[2])
            atoms=sel
            if self.use_progressBar : self._resetProgressBar(len(atoms))
            #can we reaplce the map/lambda by [[]]?
            [self._toggleUpdateSphere(x[1],display,needRedo,x[0],
                                        len(atoms),"S") for x in enumerate(atoms)]
#            map(lambda x,display=display,needRedo=needRedo,N=len(atoms): 
#                        self._toggleUpdateSphere(x[1],display,needRedo,x[0],N,"S"), 
#                        enumerate(atoms))
                        
    def _editBS(self,mol,atms,opts):
        """
        Callback for displayStickandBalls commands. Create and update the sticks
        and balls geometries
        
        @type  mol: MolKit.Protein
        @param mol: the molecule affected by the command
        @type atms: MolKit.AtomSet
        @param atms: the atom selection
        @type  opts: list
        @param opts: the list of option used for the command (only, negate, bRad,
        bScale, bquality, cradius, cquality, sticksBallsLicorice, redraw)
        """    
        
        sc = self._getCurrentScene()
        display = not opts[1]
        needRedo = opts[-1]
        options=self.mv.displaySticksAndBalls.lastUsedValues["default"]
        if options.has_key("redraw"): needRedo = options["redraw"]
        
        #NB do we want to handle multiple mol at once?
        mol = mol[0]
        root = mol.geomContainer.masterGeom.obj
        chobj = mol.geomContainer.masterGeom.chains_obj
        sel=atms[0]
        #if not hasattr(g,"obj") and display: 
        
        gb = mol.geomContainer.geoms['balls'] 
        gs = mol.geomContainer.geoms['sticks'] 
        if not hasattr(gb,"obj") and  not hasattr(gs,"obj") : 
            mol.allAtoms.ballRad = opts[2]
            mol.allAtoms.ballScale = opts[3]
            mol.allAtoms.cRad = opts[5]
            for atm in mol.allAtoms: 
                atm.colors['sticks'] = (1.0, 1.0, 1.0) 
                atm.opacities['sticks'] = 1.0 
                atm.colors['balls'] = (1.0, 1.0, 1.0) 
                atm.opacities['balls'] = 1.0	
            if opts[7] !='Sticks only' : #no balls
                if not hasattr(gb,"obj") and display: 
                    mesh=self._createBaseSphere(name=mol.name+"_b_balls",quality=opts[4],
                                                cpkRad=opts[2],scale=opts[3],
                                                radius=opts[2],parent=root) 
                    ob=self._instancesAtomsSphere("base_balls",mol.allAtoms,mesh,sc,
                                                  scale=opts[3],R=opts[2],
                                                  join=self.joins,geom=gb,
                                                  pb=self.use_progressBar) 
                    self._addObjToGeom([ob,mesh],gb)
                    """for i,o in enumerate(ob): 
                        parent=root
                        hierarchy=self._parseObjectName(o) 
                        
                        if hierarchy != "" :
                            if self.useTree == 'perRes' :
                                parent = self._getObject(mol.geomContainer.masterGeom.res_obj[hierarchy[2]])
                            elif self.useTree == 'perAtom' :
                                parent = self._getObject(o.get_name().split("_")[1])
                            else :
                                parent = self._getObject(chobj[hierarchy[1]+"_balls"])
                            #self._addObjectToScene(sc,o,parent=parent) 
                            #self._toggleDisplay(o,False)  #True per default
                            if self.use_progressBar :
                                progress = float(i) / len(ob)
                                self._progressBar(progress, 'add Balls to scene')
                    """
            if not hasattr(gs,"obj") and display: 
                set = mol.geomContainer.atoms["sticks"]
                stick=self._Tube(set,sel,gs.getVertices(),gs.getFaces(),sc, None, 
                                 res=15, size=opts[5], sc=1.,join=0,bicyl=self.bicyl,
                                 hiera =self.useTree,pb=self.use_progressBar) 
                self._addObjToGeom(stick,gs)
                #adjust the size
                #self._updateTubeMesh(gs,cradius=opts[5],quality=opts[6])
                #toggleds off while create it
                #for o in stick[0]: 
                #    self._toggleDisplay(o,False)
        #else:
        if hasattr(gb,"obj"): 
            #if needRedo : 
            self._updateSphereMesh(gb,quality=opts[4],cpkRad=opts[2],
                                           scale=opts[3],radius=opts[2])
            atoms=sel
            if self.use_progressBar : self._resetProgressBar(len(atoms))
            if opts[7] =='Sticks only' : 
                display = False 
            else :  display = display
            [self._toggleUpdateSphere(x[1],display, needRedo,x[0],
                                        len(atoms),"B") for x in enumerate(atoms)] 
#            map(lambda x,display=display,needRedo=needRedo,N=len(atoms): 
#                        self._toggleUpdateSphere(x[1],display,needRedo,x[0],N,"B"), 
#                        enumerate(atoms))

        if hasattr(gs,"obj"): 
            #first update geom
            self._updateTubeMesh(gs,cradius=opts[5],quality=opts[6])
            atoms=sel
            #set = mol.geomContainer.atoms["sticks"] 
            bonds, atnobnd = atoms.bonds
            #print len(atoms)
            #for o in gs.obj:util.toggleDisplay(o,display=False) 
            if len(atoms) > 0 :
                if self.use_progressBar : self._resetProgressBar(len(bonds))
                [self._toggleUpdateStick(x[1],display,needRedo,x[0],len(bonds),
                                           mol.name) for x in enumerate(bonds)] 
#                map(lambda x,display=display,needRedo=needRedo,N=len(bonds),molname=mol.name: 
#                        self._toggleUpdateStick(x[1],display,needRedo,x[0],N,molname), 
#                        enumerate(bonds))                
         
    def _SecondaryStructure(self,mol,atms,options,extrude=False):
        """
        Callback for display/extrudeSecondaryStructrure commands. Create and update 
        the mesh polygons for representing the secondary structure
        
        
        @type  mol: MolKit.Protein
        @param mol: the molecule affected by the command
        @type atms: MolKit.AtomSet
        @param atms: the atom selection
        @type  options: list
        @param options: the list of option used for the command (only, negate, bRad,
        bScale, bquality, cradius, cquality, sticksBallsLicorice, redraw)
        @type  extrude: boolean
        @param extrude: type of command : extrude or display
        """ 
        chname=['Z','Y','X','W','V','U','T']
        proxy = self.colorProxyObject
        self.colorProxyObject = False
        sc = self._getCurrentScene()
        mol = mol[0]
        sel=atms[0]
#        print mol, sel, len(mol.allAtoms) != len(sel)
        selection = len(mol.allAtoms) != len(sel)
        chn = sel[0].getParentOfType(Chain)
#        print chn
        root = mol.geomContainer.masterGeom.obj
        chobj = mol.geomContainer.masterGeom.chains_obj
        display = not options[1]
        i=0
        if extrude :display = options[9]
        #check the ss 
        if not hasattr(chn,"secondarystructureset"):
            return
        for ch in mol.chains:
#            print ch.name
            if selection and ch is chn:
                ch = chn
#                print chn.name
            parent = self._getObject(chobj[ch.name+"_ss"])
            for elem in ch.secondarystructureset:
                #get the geom or the extruder ?
                ex=elem.exElt
                name = elem.name
                if not hasattr(ex,"obj") and display :
                    parent=self._getObject(chobj[ch.name+"_ss"])                  
                    self.createMesh(mol.name+"_"+ch.name+"_"+name,ex,parent=parent)
                    elem.exElt.name = name
                    #change the material color to ss
                    for key in SecondaryStructureType.keys():
                        if key in name:
                            color = SecondaryStructureType[key]
                            break
                    matname = "mat_"+self.helper.getName(ex.obj)
                    self.helper.colorMaterial(matname, color)
                elif hasattr(ex,"obj") : 
                    self._updateMesh(ex) 
                    self._toggleDisplay(ex.obj,display)
            if selection :
                break
            if self.use_progressBar  and (i%20)==0 :
                progress = float(i) / 100#len(self.mv.sets.keys())
                self._progressBar(progress, 'add SS to scene')
                i+=1
        self.colorProxyObject = proxy
		                    
    def _computeMSMS(self, mol,atms,options):
        """
        Callback for computation of MSMS surface. Create and update 
        the mesh polygons for representing the MSMS surface
        
        
        @type  mol: MolKit.Protein
        @param mol: the molecule affected by the command
        @type atms: MolKit.AtomSet
        @param atms: the atom selection
        @type  options: list
        @param options: the list of option used for the command; options order : 
        surfName, pRadius, density,perMol, display, hdset, hdensity
        """ 

        name=options[0]
        mol = mol[0]
        root = mol.geomContainer.masterGeom.obj
        #chobj = mol.geomContainer.masterGeom.chains_obj
        sel=atms[0]
        parent=self.getChainParentName(sel,mol)
        if parent == None : parent=root   
        g = mol.geomContainer.geoms[name]
        if not hasattr(g,"mol"):
            g.mol = mol
        if hasattr(g,"obj") : 
            self._updateMesh(g)
        else :
            self.createMesh(name,g,parent=parent,proxyCol=True)
        if options[4] :
            self._toggleDisplay(g.obj,display=options[4]) 
            
    def _displayMSMS(self, mol,atms,options):
        """
        Callback for displayMSMS commands. display/undisplay 
        the mesh polygons representing the MSMS surface
        
        @type  mol: MolKit.Protein
        @param mol: the molecule affected by the command
        @type atms: MolKit.AtomSet
        @param atms: the atom selection
        @type  options: list
        @param options: the list of option used for the command; options order : 
        surfName, pRadius, density,perMol, display, hdset, hdensity
        """         
        #options order : surfName(names), negate, only, nbVert
        #this function only toggle the display of the MSMS polygon
        name=options[0][0] #surfName(names) is a list...
        display = not options[1]
        g = mol[0].geomContainer.geoms[name]    
        if hasattr(g,"obj") : 
            self._toggleDisplay(g.obj,display=display)

    def _colorStick(self,bds,i,atoms,N,fType,p,mol):
        """
        Handle the coloring of one bonds stick geometry.
        i and N arg are used for progress bar purpose.
        
        @type  bds: MolKit.Bonds
        @param bds: the bonds to color
        @type i: int
        @param i: the bond indice
        @type  atoms: MolKit.AtomSet
        @param atoms: the list of atoms
        @type  N: int
        @param N: the total number of bonds
        @type  fType: str
        @param fType: the colorCommand type
        @type  p: Object
        @param p: the parent object
        @type  mol: MolKit.Protein
        @param mol: the molecule parent
        """         
        atm1=bds.atom1
        atm2=bds.atom2
        if atm1 in atoms or atm2 in atoms : 
            vcolors=[atm1.colors["sticks"],atm2.colors["sticks"]]
            if not self.bicyl :
                n1=atm1.full_name().split(":")
                name="T_"+mol.name+"_"+n1[1]+"_"+util.changeR(n1[2])+"_"+n1[3]+"_"+atm2.name                
#                name="T_"+atm1.name+str(atm1.number)+"_"+atm2.name+str(atm2.number)
                o=self._getObject(name)
                if o != None :
                    self._checkChangeMaterial(o,fType,
                    atom=atm1,parent=p,color=vcolors[0])
            else :                             
                n1=atm1.full_name().split(":")
                n2=atm2.full_name().split(":")
                name1="T_"+mol.name+"_"+n1[1]+"_"+util.changeR(n1[2])+"_"+n1[3]+"_"+atm2.name
                name2="T_"+mol.name+"_"+n2[1]+"_"+util.changeR(n2[2])+"_"+n2[3]+"_"+atm1.name	                            
                o=self._getObject(name1)
                if o != None : 
                    self._checkChangeMaterial(o,fType,
                    atom=atm1,parent=p,color=vcolors[0])
                o=self._getObject(name2)
                if o != None : 
                    self._checkChangeMaterial(o,fType,
                    atom=atm2,parent=p,color=vcolors[1])
        if self.use_progressBar and (i%20)==0:
            progress = float(i) / N
            self._progressBar(progress, 'color Sticks')
 
    def _colorSphere(self,atm,i,sel,prefix,p,fType,geom):
        """
        Handle the coloring of one atom sphere geometry.
        i and N arg are used for progress bar purpose.
        
        @type  atm: MolKit.Atom
        @param atm: the atom to color
        @type i: int
        @param i: the atom indice
        @type  sel: MolKit.AtomSet
        @param sel: the list of atoms
        @type  prefix: str
        @param prefix: cpk or ball sphere geometry, ie "S" or "B"
        @type  p: Object
        @param p: the parent object
        @type  fType: str
        @param fType: the colorCommand type
        @type  geom: str
        @param geom: the parent geometry ie cpk or balls
        """         
        name = prefix+"_"+atm.full_name()
        o=self._getObject(name)
        vcolors = [atm.colors[geom],]
        if o != None :     
            self._checkChangeMaterial(o,fType,atom=atm,parent=p,color=vcolors[0])
            if self.use_progressBar  and (i%20)==0 :
                progress = float(i) / len(sel)
                self._progressBar(progress, 'color Spheres')
        
    def _color(self,mol,atms,options):
        """
        General Callback function reacting to any colorX commands. Call according
        function to change/update the object color.
        Note: should be optimized...
        
        @type  mol: MolKit.Protein
        @param mol: the molecule affected by the command
        @type atms: MolKit.AtomSet
        @param atms: the atom selection
        @type  options: list
        @param options: the list of option used for the command
        """         
        
        #color the list of geoms (options[0]) according the function (options[-1])
        lGeoms = options[0]
        fType = options[-1]
        mol = mol[0] #TO FIX
        sel=atms[0]
#        print mol, sel, len(mol.allAtoms) != len(sel)
        selection = len(mol.allAtoms) != len(sel)
        chn = sel[0].getParentOfType(Chain)
        root = mol.geomContainer.masterGeom.obj
        chobj = mol.geomContainer.masterGeom.chains_obj       
#        print chn
        for geom in lGeoms : 
            if geom=="secondarystructure" :
                #TOFIX the color/res not working...
                #gss = mol.geomContainer.geoms["secondarystructure"]
                for ch in mol.chains:
                    print ch.name
                    if selection and ch is chn:
                        ch = chn
                        print chn.name
                    parent = self._getObject(chobj[ch.name+"_ss"])
                    for elem in ch.secondarystructureset:
                        #get the geom or the extruder ?
                        ex=elem.exElt
                        name = elem.name
                        colors = elem.exElt.colors
                        if colors is None :
                            #get the regular color for this SS if none is get
                            colors = [SecondaryStructureType[SS.structureType],]
                        if hasattr(ex,"obj"):
                            self._changeColor(ex,colors,perVertex=False) #perFaces color

#                for name,g in mol.geomContainer.geoms.items() :
#                    if name[:4] in ['Heli', 'Shee', 'Coil', 'Turn', 'Stra']:      
#                        SS= g.SS
#                        name='%s%s'%(SS.name, SS.chain.id)
#                        #print name
#                        colors=mol.geomContainer.getGeomColor(name)
#                        if colors is None :
#                            #get the regular color for this SS if none is get
#                            colors = [SecondaryStructureType[SS.structureType],]
#                        flag=mol.geomContainer.geoms[name].vertexArrayFlag
#                        if hasattr(g,"obj"):
#                            self._changeColor(g,colors,perVertex=flag)   
            elif geom=="cpk" or geom=="balls": 
                #have instance materials...so if colorbyResidue have to switch to residueMaterial
                parent = self.getSelectionCommand(sel,mol)
                g = mol.geomContainer.geoms[geom]
                colors=mol.geomContainer.getGeomColor(geom)
                #or do we use the options[1] which should be the colors ?
                prefix="S"
                name="cpk"
                if geom == "balls" :
                    prefix="B"
                    name="bs"#"balls&sticks"
                if len(sel) == len(mol.allAtoms) :
                    p = mol.name+"_"+name
                else :
                    p = parent
                if hasattr(g,"obj"):
                    [self._colorSphere(x[1],x[0],sel,
                                    prefix,p,fType,geom) for x in enumerate(sel)]
#                    map(lambda x,sel=sel,prefix=prefix,p=p,fType=fType,geom=geom: 
#                        self._colorSphere(x[1],x[0],sel,prefix,p,fType,geom), 
#                        enumerate(sel))
            elif geom =="sticks" : 
                g = mol.geomContainer.geoms[geom]
                colors = mol.geomContainer.getGeomColor(geom)
                parent = self.getSelectionCommand(sel,mol)
                if hasattr(g,"obj"):
                    atoms=sel                    
                    set = mol.geomContainer.atoms["sticks"]
                    if len(set) == len(mol.allAtoms) : p = mol.name+"_cpk"
                    else : p = parent
                    bonds, atnobnd = set.bonds
                    if len(set) != 0 : 
                        [self._colorStick(x[1],x[0],atoms,len(bonds),fType,p,mol) for x in enumerate(bonds)]
#                        map(lambda x,atoms=atoms,p=p,fType=fType,mol=mol,bonds=bonds: 
#                            self._colorStick(x[1],x[0],atoms,bonds,fType,p,mol), 
#                            enumerate(bonds))
            else :
                if mol.geomContainer.geoms.has_key(geom):
                    g = mol.geomContainer.geoms[geom]
                    colors=mol.geomContainer.getGeomColor(geom)
                    flag=g.vertexArrayFlag
                    if hasattr(g,"obj"):
                        self._changeColor(g,colors,perVertex=flag,
                                              pb=self.use_progressBar)

    def _isoSurface(self,grid,options):
        """
        Callback for computing isosurface of grid volume data. will create and update
        the mesh showing the isosurface at a certain isovalue.
        
        @type  grid: Volume.Grid3D
        @param grid: the current grid volume data
        @type  options: list
        @param options: the list of option used for the command; ie isovalue, size...
        """         
        if len(options) ==0: 
            name=grid.name
            g = grid.srf
        else :
            name = options[0]
            g = grid.geomContainer['IsoSurf'][name]
            print name, g
        root = None
        if hasattr(self.mv,'cmol') and self.mv.cmol != None:
            mol = self.mv.cmol 
            root = mol.geomContainer.masterGeom.obj
        else :
            if hasattr(grid.master_geom,"obj"):
                root = grid.master_geom.obj
            else :    
                root = self._newEmpty(grid.master_geom.name)
                self._addObjectToScene(self._getCurrentScene(),root)
                self._addObjToGeom(root,grid.master_geom)
        if hasattr(g,"obj") : #already computed so need update
            sys.stderr.write("UPDATE MESH")
            self._updateMesh(g)
        else :
            self.createMesh(name,g,proxyCol=True,parent=root)

    def piecewiseLinearInterpOnIsovalue(self,x):
        """Piecewise linear interpretation on isovalue that is a function
        blobbyness.
        """
        import sys
        X = [-3.0, -2.5, -2.0, -1.5, -1.3, -1.1, -0.9, -0.7, -0.5, -0.3, -0.1]
        Y = [0.6565, 0.8000, 1.0018, 1.3345, 1.5703, 1.8554, 2.2705, 2.9382, 4.1485, 7.1852, 26.5335]
        if x<X[0] or x>X[-1]:
            print "WARNING: Fast approximation :blobbyness is out of range [-3.0, -0.1]"
            return None
        i = 0
        while x > X[i]:
            i +=1
        x1 = X[i-1]
        x2 = X[i]
        dx = x2-x1
        y1 = Y[i-1]
        y2 = Y[i]
        dy = y2-y1
        return y1 + ((x-x1)/dx)*dy
        
    def coarseMolSurface(self,molFrag,XYZd,isovalue=7.0,resolution=-0.3,padding=0.0,
                         name='CoarseMolSurface',geom=None):
        """
        Function adapted from the Vision network which compute a coarse molecular 
        surface in PMV
        
        @type  molFrag: MolKit.AtomSet
        @param molFrag: the atoms selection
        @type  XYZd: array
        @param XYZd: shape of the volume
        @type  isovalue: float
        @param isovalue: isovalue for the isosurface computation
        @type  resolution: float
        @param resolution: resolution of the final mesh
        @type  padding: float
        @param padding: the padding
        @type  name: string
        @param name: the name of the resultante geometry
        @type  geom: DejaVu.Geom
        @param geom: update geom instead of creating a new one
        
        @rtype:   DejaVu.Geom
        @return:  the created or updated DejaVu.Geom
        """         
        print molFrag
        print molFrag.top
#        self.mv.assignAtomsRadii(molFrag.top, united=1, log=0, overwrite=0)
        from MolKit.molecule import Atom
        atoms = molFrag.findType(Atom)
        coords = atoms.coords
        radii = atoms.vdwRadius
#        print len(radii),radii[0]
#        print len(coords),coords[0]
        #self.assignAtomsRadii("1xi4g", united=1, log=0, overwrite=0)
        from UTpackages.UTblur import blur
        import numpy.oldnumeric as Numeric
#        print "res",resolution
        volarr, origin, span = blur.generateBlurmap(coords, radii, XYZd,resolution, padding = 0.0)
        volarr.shape = (XYZd[0],XYZd[1],XYZd[2])
#        print volarr
        volarr = Numeric.ascontiguousarray(Numeric.transpose(volarr), 'f')
#        print volarr
    
        weights =  Numeric.ones(len(radii), typecode = "f")
        h = {}
        from Volume.Grid3D import Grid3DF
        maskGrid = Grid3DF( volarr, origin, span , h)
        h['amin'], h['amax'],h['amean'],h['arms']= maskGrid.stats()
        #(self, grid3D, isovalue=None, calculatesignatures=None, verbosity=None)
        from UTpackages.UTisocontour import isocontour
        isocontour.setVerboseLevel(0)
    
        data = maskGrid.data
    
        origin = Numeric.array(maskGrid.origin).astype('f')
        stepsize = Numeric.array(maskGrid.stepSize).astype('f')
        # add 1 dimension for time steps amd 1 for multiple variables
        if data.dtype.char!=Numeric.Float32:
#            print 'converting from ', data.dtype.char
            data = data.astype('f')#Numeric.Float32)
    
        newgrid3D = Numeric.ascontiguousarray(Numeric.reshape( Numeric.transpose(data),
                                              (1, 1)+tuple(data.shape) ), data.dtype.char)
#        print "ok"       
        ndata = isocontour.newDatasetRegFloat3D(newgrid3D, origin, stepsize)
    
#        print "pfff"
        isoc = isocontour.getContour3d(ndata, 0, 0, isovalue,
                                           isocontour.NO_COLOR_VARIABLE)
        vert = Numeric.zeros((isoc.nvert,3)).astype('f')
        norm = Numeric.zeros((isoc.nvert,3)).astype('f')
        col = Numeric.zeros((isoc.nvert)).astype('f')
        tri = Numeric.zeros((isoc.ntri,3)).astype('i')
        isocontour.getContour3dData(isoc, vert, norm, col, tri, 0)
        #print vert
    
        if maskGrid.crystal:
            vert = maskGrid.crystal.toCartesian(vert)
        
        #from DejaVu.IndexedGeom import IndexedGeom
        from DejaVu.IndexedPolygons import IndexedPolygons
        if geom == None : 
            g=IndexedPolygons(name=name)
        else :
            g = geom
        #print g
        inheritMaterial = None
        g.Set(vertices=vert, faces=tri, materials=None, 
                  tagModified=False, 
                  vnormals=norm, inheritMaterial=inheritMaterial )
        #shouldnt this only for the selection set ?
        g.mol = molFrag.top
        for a in atoms:#g.mol.allAtoms:
            a.colors[g.name] = (1.,1.,1.)
            a.opacities[g.name] = 1.0
        self.mv.bindGeomToMolecularFragment(g, atoms)
        #print len(g.getVertices())
        return g
        
    def getCitations(self):
        citation=""
        for module in self.mv.showCitation.citations:
            citation +=self.mv.showCitation.citations[module]
        return citation

    def testNumberOfAtoms(self,mol):
        nAtoms = len(mol.allAtoms)
        if nAtoms > 5000 :
            mol.doCPK = False
        else :
            mol.doCPK = True

#def piecewiseLinearInterpOnIsovalue(x):
#            """Piecewise linear interpretation on isovalue that is a function
#            blobbyness.
#            """
#            import sys
#            X = [-3.0, -2.5, -2.0, -1.5, -1.3, -1.1, -0.9, -0.7, -0.5, -0.3, -0.1]
#            Y = [0.6565, 0.8000, 1.0018, 1.3345, 1.5703, 1.8554, 2.2705, 2.9382, 4.1485, 7.1852, 26.5335]
#            if x<X[0] or x>X[-1]:
#                print "WARNING: Fast approximation :blobbyness is out of range [-3.0, -0.1]"
#                return None
#            i = 0
#            while x > X[i]:
#                i +=1
#            x1 = X[i-1]
#            x2 = X[i]
#            dx = x2-x1
#            y1 = Y[i-1]
#            y2 = Y[i]
#            dy = y2-y1
#            return y1 + ((x-x1)/dx)*dy

    #####EXTENSIONS FUNCTION
    def showMolPose(self,mol,pose,conf):
        """
        Show pyrosetta pose object which is a the result conformation of a
        simulation
        
        @type  mol: MolKit.Protein
        @param mol: the molecule node to apply the pose
        @type  pose: rosetta.Pose
        @param pose: the new pose from PyRosetta
        @type  conf: int
        @param conf: the indice for storing the pose in the molecule conformational stack        
        """
        from Pmv.moleculeViewer import EditAtomsEvent
        pmv_state = conf
        import time
        if type(mol) is str:
            model = self.getMolFromName(mol.name)
        else :
            model = mol
        model.allAtoms.setConformation(conf)
        coord = {}
        print pose.n_residue(),len(model.chains.residues)
        for resi in range(1, pose.n_residue()+1):
            res = pose.residue(resi)
            resn = pose.pdb_info().number(resi)
            #print resi,res.natoms(),len(model.chains.residues[resi-1].atoms)
            k=0
            for atomi in range(1, res.natoms()+1):
                name = res.atom_name(atomi).strip()
                if name != 'NV' :
                    a=model.chains.residues[resi-1].atoms[k]     
                    pmv_name=a.name
                    k = k + 1		 
                    if name != pmv_name : 
            	        if name[1:] != pmv_name[:-1]:
            	            print name,pmv_name
            	        else : 
            	            coord[(resn, pmv_name)] = res.atom(atomi).xyz()
            	            cood=res.atom(atomi).xyz()
            	            a._coords[conf]=[cood.x,cood.y,cood.z]
            					
                    else : 
            	         coord[(resn, name)] = res.atom(atomi).xyz()
            	         cood=res.atom(atomi).xyz()
            	         a._coords[conf]=[cood.x,cood.y,cood.z]  #return coord
        model.allAtoms.setConformation(conf)
        event = EditAtomsEvent('coords', model.allAtoms)
        self.dispatchEvent(event)
        #epmv.insertKeys(model.geomContainer.geoms['cpk'],1)
        self.helper.update()
        
    def updateDataGeom(self,mol):
        """
        Callback for updating special geometry that are not PMV generated and which
        do not react to editAtom event. e.g. pointCloud or Spline
        
        @type  mol: MolKit.Protein
        @param mol: the parent molecule
        """         
        
        mname = mol.name
        disp = self.mv.molDispl[mname]
        if disp.has_key("loft"):
            if disp["loft"] :
                #verify in c4d and blender
                self.helper.update_spline("loft"+mol.name+"_spline",mol.allAtoms.get("CA").coords)        
        for c in mol.chains :
            if disp.has_key("spline"):
                if disp["spline"] :
                    self.helper.update_spline(mol.name+"_"+c.name+"spline",c.residues.atoms.get("CA").coords)

            if self.doCloud : 
                self.helper.updatePoly(mol.name+":"+c.name+"_cloud",vertices=c.residues.atoms.coords)
            #look if there is a msms:
#        #find a way to update MSMS and coarse
#        if self.mv.molDispl[mname][3] : self.gui.updateSurf()
#        if self.mv.molDispl[mname][4] : self.gui.updateCoarseMS()
    
    def updateData(self,traj,step):
        """
        Callback for updating molecule data following the data-player.
        DataType can be : MD trajectory, Model Data (NMR, DLG, ...)
        
        @type  traj: array
        @param traj: the current trajectory object. ie [trajData,trajType]
        @type  step: int or float
        @param step: the new value to apply
        """         
         
        if traj[0] is not None :
            if traj[1] == 'traj':
                mol = traj[0].player.mol
                maxi=len(traj[0].coords)
                mname = mol.name
                if step < maxi :
                    traj[0].player.applyState(int(step))
                    self.updateDataGeom(mol)
            elif traj[1] == "model":
                mname = traj[0].split(".")[0]
                type = traj[0].split(".")[1]
                mol = self.mv.getMolFromName(mname)
                if type == 'model':
                    nmodels=len(mol.allAtoms[0]._coords)
                    if step < nmodels:
                        mol.allAtoms.setConformation(step)
                        #self.mv.computeSecondaryStructure(mol.name,molModes={mol.name:'From Pross'})
                        from Pmv.moleculeViewer import EditAtomsEvent                       
                        event = EditAtomsEvent('coords', mol.allAtoms)
                        self.mv.dispatchEvent(event)
                        self.updateDataGeom(mol)
                else :
                    nmodels=len(mol.docking.ch.conformations)
                    if step < nmodels:
                        mol.spw.applyState(step)
                        self.updateDataGeom(mol)

    def updateTraj(self,traj):
        """
        Callback for updating mini,maxi,default,step values needed by the data player
        DataType can be : MD trajectory, Model Data (NMR, DLG, ...)
        
        @type  traj: array
        @param traj: the current trajectory object. ie [trajData,trajType]
        """         
        
        if traj[1] == "model":
            mname = traj[0].split(".")[0]
            type = traj[0].split(".")[1]
            mol = self.mv.getMolFromName(mname)
            if type == 'model':
                nmodels=len(mol.allAtoms[0]._coords)
            else :
                nmodels=len(mol.docking.ch.conformations)
            mini=0
            maxi=nmodels
            default=0
            step=1
        elif  traj[1] == "traj":
            mini=0
            maxi=len(traj[0].coords)
            default=0
            step=1
        elif  traj[1] == "grid":
            mini=traj[0].mini
            maxi=traj[0].maxi
            default=traj[0].mean
            step=0.01
        return mini,maxi,default,step
        

    def renderDynamic(self,traj,timeWidget=False,timeLapse=5):
        """
        Callback for render a full MD trajectory.
        
        @type  traj: array
        @param traj: the current trajectory object. ie [trajData,trajType]
        @type  timeWidget: boolean
        @param timeWidget: use the timer Widget to cancel the rendering
        @type  timeLapse: int
        @param timeLapse: the timerWidget popup every timeLapse
        """                 
        if timeWidget:
            dial= self.helper.TimerDialog()
            dial.cutoff = 15.0
        if traj[0] is not None :
            if traj[1] == 'traj':
                mol = traj[0].player.mol
                maxi=len(traj[0].coords)
                mname = mol.name
                for i in range(maxi):
                    if timeWidget and (i % timeLapse) == 0 :
                        dial.open()
                        if dial._cancel :
                            return False
                    traj[0].player.applyState(i)
                    self.updateDataGeom(mol)
                    if self.mv.molDispl[mname]["surf"] : self.gui.updateSurf()
                    if self.mv.molDispl[mname]["cms"] : self.gui.updateCoarseMS()                    
                    self.helper.update()
                    self._render("md%.4d" % i,640,480)
            elif traj[1] == 'model':
                mname = traj[0].split(".")[0]
                type = traj[0].split(".")[1]
                mol = self.mv.getMolFromName(mname)
                if type == 'model':
                    maxi=len(mol.allAtoms[0]._coords)
                    for i in range(maxi):
                        mol.allAtoms.setConformation(step)
                        #self.mv.computeSecondaryStructure(mol.name,molModes={mol.name:'From Pross'})
                        from Pmv.moleculeViewer import EditAtomsEvent                       
                        event = EditAtomsEvent('coords', mol.allAtoms)
                        self.mv.dispatchEvent(event)
                        self.updateDataGeom(mol)
                        if self.mv.molDispl[mname]["surf"] : self.gui.updateSurf()
                        if self.mv.molDispl[mname]["cms"] : self.gui.updateCoarseMS()
                        self.helper.update()
                        self._render("model%.4d" % i,640,480)

        
        
    def APBS(self):
        """ DEPRECATED AND NOT USE """
        #need the pqrfile
        #then can compute
        self.mv.APBSSetup.molecule1Select(molname)
        self.mv.APBSSetup({'solventRadius':1.4,'ions':[],'surfaceCalculation':
            'Cubic B-spline',
            'pdb2pqr_Path':'/Library/MGLTools/1.5.6.up/MGLToolsPckgs/MolKit/pdb2pqr/pdb2pqr.py',
            'xShiftedDielectricFile':'',
            'proteinDielectric':2.0,
            'projectFolder':'apbs-project',
            'zShiftedDielectricFile':'',
            'complexPath':'','splineBasedAccessibilityFile':'',
            'chargeDiscretization':'Cubic B-spline',
            'ionAccessibilityFile':'','gridPointsY':65,
            'chargeDistributionFile':'','ionChargeDensityFile':'',
            'pdb2pqr_ForceField':'amber','energyDensityFile':'',
            'fineCenterZ':22.6725,'forceOutput':'','fineCenterX':10.0905,
            'fineCenterY':52.523,'potentialFile':'OpenDX','splineWindow':0.3,
            'yShiftedDielectricFile':'','VDWAccessibilityFile':'',
            'gridPointsX':65,'molecule1Path':'/Users/ludo/1M52mono.pqr',
            'sdens':10.0,'coarseLengthY':73.744,
            'boundaryConditions':'Single Debye-Huckel',
            'calculationType':'Electrostatic potential',
            'fineLengthZ':73.429,'fineLengthY':52.496,
            'fineLengthX':68.973,'laplacianOfPotentialFile':'',
            'saltConcentration':0.01,'pbeType':'Linearized','coarseCenterX':10.0905,
            'coarseCenterZ':22.6725,'ionNumberFile':'','coarseCenterY':52.523,
            'name':'Default','solventDielectric':78.54,'solventAccessibilityFile':'',
            'APBS_Path':'/Library/MGLTools/1.5.6.up/MGLToolsPckgs/binaries/apbs',
            'molecule2Path':'','coarseLengthX':98.4595,'kappaFunctionFile':'',
            'coarseLengthZ':105.1435,'systemTemperature':298.15,'gridPointsZ':65,
            'energyOutput':'Total'}, log=0)
        #then run
        self.mv.APBSRun('1M52mono', None, None, APBSParamName='Default', 
                     blocking=False, log=0)
        #then read the dx grid
        self.Grid3DReadAny('/Library/MGLTools/1.5.6.up/bin/apbs-1M52mono/1M52mono.potential.dx', 
                           normalize=False, log=0, show=False)
                           
        #self.APBSMapPotential2MSMS(potential='/Library/MGLTools/1.5.6.up/bin/apbs-1M52mono/1M52mono.potential.dx', log=0, mol='1M52mono')

    def APBS2MSMS(self,grid,surf=None,offset=1.0,stddevM=5.0):
        """
        Map a surface mesh using grid (APBS,AD,...) values projection.
        This code is based on the Pmv vision node network which color a MSMS using a APBS computation.
        
        @type  grid: grids3D
        @param grid: the grid to project
        @type  surf: DejaVu.Geom or hostApp mesh
        @param surf: the surface mesh to color
        @type  offset: float
        @param offset: the offset to apply to the vertex normal used for the projection
        @type  stddevM: float
        @param stddevM: scale factor for the standard deviation fo the grid data values
        """                 
        
        v, f,vn,fn =self.getSurfaceVFN(surf)
        if v is None : return
        points = v+(vn*offset)
        data = self.TriInterp(grid,points)
        #need to apply some stddev on data
        datadev = util.stddev(data)*stddevM
        #need to make a colorMap from this data
        #colorMap should be the rgbColorMap
        from Pmv import hostappInterface
        cmap = hostappInterface.__path__[0]+"/apbs_map.py"
        lcol = self.colorMap(colormap='rgb256',mini=-datadev,
                             maxi=datadev,values=data,filename=cmap)
        if self.soft =="c4d":
            self._changeColor(surf,lcol,proxyObject=True)
        else :
            self._changeColor(surf,lcol)

    def getSurfaceVFN(self,geometry):
        """
        Extract vertices, faces and normals from either an DejaVu.Geom
        or a hostApp polygon mesh
        
        @type  geometry: DejaVu.Geom or hostApp polygon
        @param geometry: the mesh to decompose
        
        @rtype:   list
        @return:  faces,vertices,vnormals of the geometry
        """         
        
        if geometry:
            if not hasattr(geometry,'asIndexedPolygons'):
                f=None
                v=None
                vn=None
                f,v,vn = self.helper.DecomposeMesh(geometry,edit=False,
                                                    copy=False,tri=False,
                                                    transform=False)
                fn=None
            else :
                geom = geometry.asIndexedPolygons()
                v = geom.getVertices()
                vn = geom.getVNormals()
                fn = geom.getFNormals()
                f = geom.getFaces()
            return Numeric.array(v), f,Numeric.array(vn),fn
        
    def TriInterp(self,grid,points):
        """
        Trilinear interpolation of a list of point in the given grid.
        
        @type  grid: grid3D
        @param grid: the grid object
        @type  points: numpy.array
        @param points: list of point to interpolate in the grid
        
        @rtype:   list
        @return:  the interpolated value for the given list of point
        """         
        
        values = []
        import numpy.oldnumeric as N
        from Volume.Operators.trilinterp import trilinterp
        
        origin = N.array(grid.origin, Numeric.Float32)
        stepSize = N.array(grid.stepSize, Numeric.Float32)

        invstep = ( 1./stepSize[0], 1./stepSize[1], 1./stepSize[2] )

        if grid.crystal:
            points = grid.crystal.toFractional(points)

        values = trilinterp(points, grid.data, invstep, origin)
    
        return values

    def colorMap(self, colormap='rgb256', values=None, mini=None, maxi=None,filename=None):
        """
        Prepare and setup a DejaVu.colorMap using the given options 
        
        @type  colormap: str
        @param colormap: name of existing colormap
        @type  values: list
        @param values: list of color for the colormap
        @type  mini: float
        @param mini: minimum value for the ramp
        @type  maxi: float
        @param maxi: maximum value for the ramp
        @type  filename: str
        @param filename: colormap filename 
        
        @rtype:   DejaVu.colorMap
        @return:  the prepared color map
        """         
        from DejaVu.colorMap import ColorMap
        import types
        if colormap is None:
            pass#colormap = RGBARamp
        elif type(colormap) is types.StringType \
          and self.mv.colorMaps.has_key(colormap):
            colormap = self.mv.colorMaps[colormap]
        if not isinstance(colormap, ColorMap):
            return 'ERROR'
        if values is not None and len(values)>0:
            if mini is None:
                mini = min(values)
            if maxi is None:
                maxi = max(values)
            colormap.configure(mini=mini, maxi=maxi)
        if filename :
            colormap.read(filename)
            colormap.configure(mini=mini, maxi=maxi)
        if (values is not None) and (len(values) > 0) :
            lCol = colormap.Map(values)
            if lCol is not None:
                return lCol.tolist()
        elif len(colormap.ramp) == 1:
            return colormap.ramp[0]
        else:
            return colormap.ramp
            
    def setEnvPyRosetta(self,extensionPath):
        #path = epmv.gui.inst.extdir[1]
        #epmv.setEnvPyRosetta(path)
        os.environ["PYROSETTA"]=extensionPath
        os.environ["PYROSETTA_DATABASE"]=extensionPath+os.sep+"minirosetta_database"
        if not os.environ.has_key("DYLD_LIBRARY_PATH"):
            os.environ["DYLD_LIBRARY_PATH"]=""
        os.environ["DYLD_LIBRARY_PATH"]=extensionPath+":"+extensionPath+"/rosetta:"+os.environ["DYLD_LIBRARY_PATH"]
        if not os.environ.has_key("LD_LIBRARY_PATH"):
            os.environ["LD_LIBRARY_PATH"]=""
        os.environ["LD_LIBRARY_PATH"]=extensionPath+"/rosetta:"+os.environ["LD_LIBRARY_PATH"]
        #this is not working! how can I do it

    def checkExtension(self):
#        global _modeller,_useModeller,_AF,_AR,_inst
        listExtension=[]
        if self.inst is None:
            self.setupInst()
        self.inst.getExtensionDirFromFile()
        for i,ext in enumerate(self.inst.extensions):
            if self.inst.extdir[i] not in sys.path :
                sys.path.append(self.inst.extdir[i])
                if ext.lower() == 'modeller' : #what about windows? doesnt matter
                    sys.path.append(self.inst.extdir[i]+"/python2.5")
        if not self.useModeller :
            try :
                import modeller
                self._modeller = True
                listExtension.append('modeller')
            except:
                print "noModeller"
        if not self._AF:
            try :
                import AutoFill
                self._AF = True
                listExtension.append('AutoFill')
            except:
                print "noAutoFill"
        if not self._AR:
            try :
                import ARViewer
                self._AR = True
                listExtension.append('ARViewer')
            except:
                print "noARViewer"
        return listExtension

    #from the helper, may change in c4d, maya to check
    
    def getGeomName(self,geom):
        g = geom
        name = "Pmv_"
        while g != geom.viewer.rootObject:
            # g.name can contain whitespaces which we have to get rid of
            gname = string.split(g.name)
            ggname = "" 
            for i in gname:
                ggname = ggname + i
                name = name + string.strip(ggname)+"AT"+\
            string.strip(str(g.instanceMatricesIndex))+ '_'
            g = g.parent
            name=string.replace(name,"-","_")
        return name
        
    def findatmParentHierarchie(self,atm,indice,hiera):
        if indice == "S" : n='cpk'
        else : n='balls'
        mol=atm.getParentOfType(Protein)
        hierarchy=self.parseObjectName(indice+"_"+atm.full_name())
        if hiera == 'perRes' :
            parent = self.helper.getObject(mol.geomContainer.masterGeom.res_obj[hierarchy[2]])
        elif hiera == 'perAtom' :
            if atm1.name in backbone : 
                parent = self.helper.getObject(atm.full_name()+"_bond")
            else :
                parent = self.helper.getObject(atm.full_name()+"_sbond")
        else :
            ch = atm.getParentOfType(Chain)
            parent=self.helper.getObject(mol.geomContainer.masterGeom.chains_obj[ch.name+"_"+n])        
        return parent

    def parseObjectName(self,o):
        if type(o) == str : name=o
        else : name=self.helper.getName(o)
        tmp=name.split("_")
        if len(tmp) == 1 : #no "_" so not cpk (S_) or ball (B_) stick (T_) or Mesh (Mesh_)
            return ""
        else :
            if tmp[0] == "S" or tmp[0] == "B" : #balls or cpk
                if len(tmp) == 3 : #molname include '_'
                    hiearchy=name[2:].split(":")
                else :           
                    hiearchy=tmp[1].split(":") #B_MOL:CHAIN:RESIDUE:ATOMS        
                return hiearchy
        return ""
        
    def parseName(self,o):
        if type(o) == str : name=o
        else : name=self.helper.getName(o)
        tmp=name.split("_")
        if len(tmp) == 1 : #molname
            hiearchy=name.split(":")
            if len(hiearchy) == 1 : return [name,""]
            else : return hiearchy
        else :
            hiearchy=tmp[0].split(":") #B_MOL:CHAIN:RESIDUE:ATOMS        
            return hiearchy

    def splitName(self,name):
    #general function-> in the adaptor ?
        if name[0] == "T" : #sticks name.. which is "T_"+chname+"_"+Resname+"_"+atomname+"_"+atm2.name\n'
            tmp=name.split("_")
            return ["T",tmp[1],tmp[2],tmp[3][0:1],tmp[3][1:],tmp[4]]
        else :
            tmp=name.split(":")
            indice=tmp[0].split("_")[0]
            molname=tmp[0].split("_")[1]
            chainname=tmp[1]
            residuename=tmp[2][0:3]
            residuenumber=tmp[2][3:]
            atomname=tmp[3]
            return [indice,molname,chainname,residuename,residuenumber,atomname]

    def _addObjToGeom(self,obj,geom):
        if type(obj) == list or type(obj) == tuple:
            if len(obj) > 2: geom.obj=obj
            elif len(obj) == 1: 
                geom.obj=self.helper.getName(obj[0])
                geom.mesh=self.helper.getName(obj[0])
            elif len(obj) == 2:
                if type(obj[0]) == list or type(obj[0]) == tuple:    
                    geom.obj=[]
                    if type(obj[1]) == list or type(obj[1]) == tuple: 
                        geom.mesh=obj[1][:]
                    elif type(obj[1]) == dict :
                        geom.mesh={}                                                
                        for me in obj[1].keys():
                            geom.mesh[me]=self.helper.getName(obj[1][me])
                    else :
                        geom.mesh=self.helper.getName(obj[1])
                    geom.obj= obj[0][:]
                else :
                    geom.mesh=self.helper.getName(obj[1])
                    geom.obj=self.helper.getName(obj[0])
        else : geom.obj=self.helper.getName(obj)

    
    def setupMaterials(self):
        #Atoms Materials
        self.helper.addMaterialFromDic(AtomElements)
        self.helper.addMaterialFromDic(DavidGoodsell)
        self.helper.addMaterial("A",(0.8,1.,1.))
        self.helper.addMaterial("anyatom",(0.8,1.,1.))
        self.helper.addMaterial("M",(0.8,1.,1.))
        self.helper.addMaterial("Mg",(0.8,1.,1.))
        self.helper.addMaterial("hetatm",(0.,1.,0.))
        self.helper.addMaterial("sticks",(0.,1.,0.))
        #Residues Materials  
        self.RasmolAminocorrected=RasmolAmino.copy()
        for res in RasmolAminoSortedKeys:
            name=res.strip()
            if name in ['A', 'C', 'G', 'T', 'U']:
                name = 'D'+name
                self.RasmolAminocorrected[name]= RasmolAmino[res]
                del self.RasmolAminocorrected[res]
        self.helper.addMaterialFromDic(self.RasmolAminocorrected)
        #SS Material
        SecondaryStructureType['Sheet']=SecondaryStructureType['Strand']
        ssc={}
        for ss in SecondaryStructureType:
            ssc[ss[:4]] = SecondaryStructureType[ss]
        self.helper.addMaterialFromDic(ssc)

    def getAtomMaterial(self,atomname):
        mat= self.helper.getMaterial("anyatom")
        try :
            if atomname not in AtomElements.keys() and \
                atomname not in DavidGoodsell.keys() and \
                atomname != 'M':
                mat= self.helper.getMaterial('A')
            else :
                mat= self.helper.getMaterial("anyatom")
            return mat
        except :
            return None

    def _checkChangeMaterial(self,o,typeMat,atom=None,parent=None,color=None):
        #print typeMat
        #print "checkChangeMaterial"
        matlist = self.helper.getAllMaterials()
        ss="Helix"
        mol = None
        ch = None
        if atom is not None :
            res=atom.getParentOfType(Residue)
            ch = atom.getParentOfType(Chain)
            mol = atom.getParentOfType(Protein)
            if hasattr(res,'secondarystructure') : ss=res.secondarystructure.name
        mats=self.helper.getMaterialObject(o)
        print "object to color", o
        print mats
        if mats is None or not mats:  
            matname=""
        else : 
            matname=self.helper.getMaterialName(mats[0])
            #difficule to get the active one so just says ""
            if self.host == 'maya' : 
                matname = ""
        names=self.splitName(self.helper.getName(o))
        
        print "current mat ", matname
        newmat = None
        self.changeMaterialSchemColor(typeMat)
        if typeMat == "" :#material by colorname-> function from rgb give color name...
            mat = self.helper.retrieveColorMat(color)
            if mat is None :  
                mat = self.helper.getMaterial("rgb"+str(color[0])[0:3]+"_"+\
                                str(color[1])[0:3]+"_"+str(color[2])[0:3])
                if mat is None :
                    mat = self.helper.addMaterial("rgb"+str(color[0])[0:3]+\
                        "_"+str(color[1])[0:3]+"_"+str(color[2])[0:3],color)
            self.helper.assignMaterial(o,[mat])
            newmat = mat
        elif typeMat == "ByProp" : #color by color
#                if parent != None : 
#                    requiredMatname = 'mat'+parent#.name #exemple mat_molname_cpk
#                else : 
#                    requiredMatname = 'mat'+self.getName(o)##exemple mat_coil1a_molname
#                if typeMat == "ByProp": 
            requiredMatname = 'mat'+self.helper.getName(o)
            print 'required ',requiredMatname
            #print parent.name,o.name,requiredMatname
            if matname != requiredMatname : 
                 #print requiredMatname
                if requiredMatname not in matlist: 
                    mat = self.helper.addMaterial(requiredMatname,color)
                    self.helper.assignMaterial(o,[mat])
                else : 
                    self.helper.colorMaterial(requiredMatname,color)
                    mat = self.helper.getMaterial(requiredMatname)
                    if mat is None:
                        mat = self.helper.addMaterial(requiredMatname,color)
                    self.helper.assignMaterial(o,[mat])
            else : 
                self.helper.colorMaterial(requiredMatname,color)
            newmat = requiredMatname
        elif typeMat == "ByAtom" :
            print matname
            if str(matname) not in self.AtmRadi.keys() : #switch to atom materials
                if names[5][0] not in AtomElements.keys() : 
                    self.helper.assignMaterial(o,[self.helper.getMaterial('A')])
                else :
                    mat = self.helper.getMaterial(names[5][0])
                    self.helper.assignMaterial(o,[self.helper.getMaterial(names[5][0])])
#            else :
#                self.helper.colorMaterial(matname,AtomElements[names[5][0]])
            newmat = names[5][0]
        elif typeMat =="AtomsU" :
            name = self.lookupDGFunc(atom)
            if name not in DavidGoodsell.keys() : 
                self.helper.assignMaterial(o,[self.helper.getMaterial('A')])
            else :            
                self.helper.assignMaterial(o,[self.helper.getMaterial(name)])
        elif typeMat == "ByResi" or typeMat == "Residu":
            rname = res.type.replace(" ","")
            if rname in ['A', 'C', 'G', 'T', 'U'] :
                rname = 'D'+rname            
            if matname not in self.RasmolAminocorrected.keys():
                if rname not in self.RasmolAminocorrected.keys(): rname='hetatm'
                self.helper.assignMaterial(o,[self.helper.getMaterial(rname)])
            newmat = rname
        elif typeMat == "BySeco" :
            if matname not in self.ssk : #switch to ss materials
                self.helper.assignMaterial(o,[self.helper.getMaterial(ss[0:4])])
            newmat = ss[0:4]
        elif typeMat == "ByChai" :
            if matname is not self.helper.getMaterialName(ch.material) : #switch to ch materials
                self.helper.assignMaterial(o,[ch.material])
            newmat = ch.material

        #assign linking material for object
#        if self.host == 'maya' :
#            name = atom.name[0]
#            if name not in AtomElements.keys() : 
#                    name = 'A'
#            self.helper.connectAttr("crn_b_cpk_"+name+"Shape",material=mat)
                    
    def changeMaterialSchemColor(self,typeMat):
        if typeMat == "ByAtom":
            [self.helper.colorMaterial(atms,AtomElements[atms]) for atms in AtomElements.keys()]
        elif typeMat == "AtomsU" :
            [self.helper.colorMaterial(atms,DavidGoodsell[atms]) for atms in DavidGoodsell.keys()] 
        elif typeMat == "ByResi":
            [self.helper.colorMaterial(res.strip(),self.RasmolAminocorrected[res]) \
               for res in self.RasmolAminocorrected.keys() ]
        elif typeMat == "Residu":
            [self.helper.colorMaterial(res,Shapely[res]) for res in Shapely.keys()] 
        elif typeMat == "BySeco":
            [self.helper.colorMaterial(ss[0:4],SecondaryStructureType[ss]) \
                for ss in SecondaryStructureType.keys()] 
        else : pass

    
    def oneStick(self,atm1,atm2,hiera,instance,parent):
        #mol=atm1.getParentOfType(Protein)
        c0=numpy.array(atm1.coords)
        c1=numpy.array(atm2.coords)
        name="T_"+atm1.name+str(atm1.number)+"_"+atm2.name+str(atm2.number)
        mat = self.helper.getMaterial('sticks')
        obj=self.helper.oneCylinder(name,c0,c1,instance,material=mat)
        if parent is not None : self.helper.reParent([obj,],parent)
        self.helper.toggleDisplay(obj,display=False)
        return obj

    def biStick(self,atm1,atm2,hiera,instance,parent):
        mol=atm1.getParentOfType(Protein)
        c0=numpy.array(atm1.coords)
        c1=numpy.array(atm2.coords)
        vect = c1 - c0
    #    name1="T_"+atm1.full_name()+"_"+atm2.name
    #    name2="T_"+atm2.full_name()+"_"+atm1.name
        n1=atm1.full_name().split(":")
        n2=atm2.full_name().split(":")
        #should use the 1lettercode for residues to gain some space
        #ResidueSetSelector.r_keyD
        
        name1="T_"+mol.name+"_"+n1[1]+"_"+util.changeR(n1[2])+"_"+n1[3]+"_"+atm2.name
        name2="T_"+mol.name+"_"+n2[1]+"_"+util.changeR(n2[2])+"_"+n2[3]+"_"+atm1.name	        
    #    name1="T_"+n1[1]+"_"+n1[2]+"_"+n1[3]+"_"+atm2.name
    #    name2="T_"+n2[1]+"_"+n2[2]+"_"+n2[3]+"_"+atm1.name
        if atm1.name[0] not in AtomElements.keys() : atN="A"
        else : atN = atm1.name[0]
        mat = self.helper.getMaterial(atN)
        if mat == None :
            mat = self.helper.addMaterial(atm1.name[0],[0.,0.,0.])
        obj1=self.helper.oneCylinder(name1,c0,(c0+(vect/2.)),instance,material=mat)
        if atm2.name[0] not in AtomElements.keys() : atN="A"
        else : atN = atm2.name[0]
        mat = self.helper.getMaterial(atN)
        if mat == None :
            mat = self.helper.addMaterial(atm2.name[0],[0.,0.,0.])
        obj2=self.helper.oneCylinder(name2,(c0+(vect/2.)),c1,instance,material=mat)
        if parent is not None : self.helper.reParent([obj1,obj2],parent)
        self.helper.toggleDisplay(obj1,display=False)
        self.helper.toggleDisplay(obj2,display=False)
        return [obj1,obj2]        

    def _Tube(self,set,sel,points,faces,scn,armObj,res=32,size=0.25,sc=2.,join=0,
             instance=None,hiera = 'perRes',bicyl=False,pb=False):
        sc=self.helper.getCurrentScene()
        sticks=[]
        bonds, atnobnd = sel.bonds
        instance=None
        mol = bonds[0].atom1.top
        if instance == None:
            #create mesh_baseBond
            parent=self.helper.newEmpty(mol.name+"_b_sticks")
            self.helper.addObjectToScene(sc,parent,
                        parent=mol.geomContainer.masterGeom.obj)
            self.helper.toggleDisplay(parent,False)
            instance=self.helper.newEmpty(mol.name+"_b_sticks_shape")
            self.helper.addObjectToScene(sc,instance,parent=parent)
            cyl = self.helper.Cylinder(mol.name+"_b_sticks_o",res=res)
            self.helper.reParent(cyl,instance)
#            self.helper.toggleDisplay(cyl,display=False)
            if self.host == "blender":
                baseCyl= self.helper.Cylinder("baseCyl",radius=1.,length=1.,res=res)
                self.helper.toggleDisplay(baseCyl,display=False)
                instance = self.helper.getMesh("mesh_"+mol.name+"_b_sticks_o")
            elif self.host == "maya":
#                self.helper.toggleDisplay(cyl,display=False)
                instance = cyl
            elif self.host == "c4d": 
                instance = parent
        for c in mol.chains:
            stick=[]
            bonds, atnobnd = c.residues.atoms.bonds
            #parent = self.findatmParentHierarchie(bonds[0].atom1,'B',hiera)
            parent=self.helper.getObject(mol.geomContainer.masterGeom.chains_obj[c.name+"_balls"])        
            print c,parent
            oneparent=True
            for i,bond in enumerate(bonds):
#                p = self.findatmParentHierarchie(bond.atom1,'B',hiera)
#                print "p", parent
#                if p != parent : 
#                    cp = p
#                    oneparent=False
#                else : cp = parent
                if bicyl :
                    stick.extend(self.biStick(bond.atom1,bond.atom2,
                                hiera,instance,parent=parent))
                else :
                    stick.append(self.oneStick(bond.atom1,bond.atom2,
                                hiera,None,parent=parent))
                if pb and (i%50) == 0:
                    progress = float(i) / len(bonds)
                    self._progressBar(progress, 'creating bonds sticks')
                    #self.gui.ProgressBar(progress, 'creating bonds sticks')
#            if oneparent :
#                self.helper.reParent(stick,parent)
            sticks.extend(stick)
        return [sticks,instance]

    def _updateMesh(self,geom):
        mesh=self.helper.getMesh(geom.mesh)
        if not hasattr(geom,"getVertices"):
            #this os probably a extEl then just get vertices and faces
            vertices = geom.vertices
            faces = geom.faces
        else :
            vertices =geom.getVertices()
            faces =  geom.getFaces()        
        self.helper.updateMesh(mesh,vertices=vertices,
                               faces = faces)
        
    def _updateTubeMesh(self,geom,quality=0.0,cradius=1.0):
        self.helper.updateTubeMesh(geom.mesh,basemesh="mesh_baseCyl",
                                   cradius=cradius,quality=quality)        
               
    def _updateSphereMesh(self,geom,quality=0.0,cpkRad=0.0,scale=1.0,radius=None):
        #compute the scale transformation matrix
        if not hasattr(geom,'mesh') : return
        """segments=quality*5
        rings=quality*5
        if quality == 0 : 
            segments = 25
            rings = 25"""
        #names=NMesh.GetNames()
        for name in geom.mesh.values(): 
            print name
#            basemesh =  self.helper.getMesh("mesh_basesphere")
            if name[-1] not in self.AtmRadi :
                name="A"
            factor=float(cpkRad)+float(self.AtmRadi[name[-1]])*float(scale)                
            self.helper.updateSphereMesh(name,basemesh="mesh_basesphere",scale=factor)

    def updateMolAtomCoord(self,mol,index=-1,types='cpk'):
        #just need that cpk or the balls have been computed once..
        #balls and cpk should be linked to have always same position
        # let balls be dependant on cpk => contraints? or update
        # the idea : spline/dynamic move link to cpl whihc control balls
        # this should be the actual coordinate of the ligand
        # what about the rc...
        if index == -1 : index = 0	
        if types == 'cpk':
            vt=self.updateMolAtomCoordCPK(mol)
            mol.allAtoms.updateCoords(vt,ind=index)
        elif types == 'lines':
            vt=self.updateMolAtomCoordLines(mol)
            mol.allAtoms.updateCoords(vt,ind=index)
        elif types == 'bones':
            vt=self.updateMolAtomCoordBones(mol)
            mol.allAtoms.get("CA").updateCoords(vt,ind=index)
        elif types =='spline':
            vt=self.updateMolAtomCoordSpline(mol)
            mol.allAtoms.get("CA").updateCoords(vt,ind=index)

    def updateMolAtomCoordCPK(self,mol):
        """
        Return each CPK spheres absolute position for the specified mol.
    
        @type  mol: Molkit protein
        @param mol: the molecule from which the cpk sphere position will be get.
        @rtype:   array
        @return:  the xyz positions coordinates  of the CPK spheres
        """
        sph = mol.geomContainer.geoms['cpk'].obj
        vt=[self.helper.ToVec(self.helper.getTranslation(x)) for x in sph]
        print vt[0]
        return vt

    def updateCoordFromObj(self,sel,debug=True):
        mv = self.mv
        s=None
        if len(sel):
            #take first object selected?
            s=sel[0]
            print "in epmv ",s
            print "of type ", self.helper.getType(s)
        if s is not None :
            #print s.GetName()
            if self.helper.getType(s) == self.helper.SPLINE :
                print "ok Spline"
                #select = s.GetSelectedPoints()#mode=P_BASESELECT)#GetPointAllAllelection();
                #print nb_points
                #selected = select.get_all(s.GetPointCount()) # 0 uns | 1 selected
                #print selected
                #assume one point selected ?
                #selectedPoint = selected.index(1)           
                #updateRTSpline(s,selectedPoint)
            if  self.helper.getType(s) == self.helper.EMPTY or \
                    self.helper.getType(s) == self.helper.INSTANCE or \
                    self.helper.getType(s) == self.helper.SPLINE:
                print "ok null" 
                #molname or molname:chainname or molname:chain_ss ...
                hi = self.parseName(self.helper.getName(s))
                #print "parsed ",hi
                if len(hi) == 1:
                    hi=[hi[0],""]
                molname = hi[0]
                chname = hi[1]
                #mg = s.GetMg()
                #should work with chain level and local matrix
                #mg = ml = s.get_ml()
                #print molname
                #print mg
                #print ml
                if hasattr(mv,'energy') : #ok need to compute energy
                    #first update obj position: need mat_transfo_inv attributes at the mollevel
                    #compute matrix inverse of actual position (should be the receptor...)
                    if hasattr(mv.energy,'amber'): 
                    #first update obj position: need mat_transfo_inv attributes at the mollevel
                        mol = mv.energy.mol
                        if mol.name == molname :
                            if mv.minimize == True:								
                                amb = mv.Amber94Config[mv.energy.name][0]			
                                self.updateMolAtomCoord(mol,index=mol.cconformationIndex)
                                #mol.allAtoms.setConformation(mol.cconformationIndex)
                                #from Pmv import amberCommands
                                #amberCommands.Amber94Config = {}
                                #amberCommands.CurrentAmber94 = {}
    							#amb_ins = Amber94(atoms, prmfile=filename)
                                mv.setup_Amber94(mol.name+":",mv.energy.name,mol.prname,indice=mol.cconformationIndex)
                                mv.minimize_Amber94(mv.energy.name, dfpred=10.0, callback_freq='10', callback=1, drms=1e-06, maxIter=100., log=0)
                                #mv.md_Amber94(mv.energy.name, 349, callback=1, filename='0', log=0, callback_freq=10)
                                #print "time"
                                #import time
                                #time.sleep(1.)
                                #mol.allAtoms.setConformation(0)
                                #mv.minimize = False
                    else :						
                        rec = mv.energy.current_scorer.mol1
                        lig = mv.energy.current_scorer.mol2
                        if rec.name == molname or lig.name == molname:
                            self.updateMolAtomCoord(rec,rec.cconformationIndex,types='cpk')
                            #mv.displayCPK(rec,redo=1)
                            self.updateMolAtomCoord(lig,lig.cconformationIndex,types='cpk')
                        if mv.energy.realTime:
                            if hasattr(mv,'art'):
                                if not mv.art.frame_counter % mv.art.nrg_calcul_rate:
                                    self.get_nrg_score(mv.energy)
                            else :
                                self.get_nrg_score(mv.energy)
                        #should we try to optimize here, lets try the rec
                        if hasattr(rec,'pmvaction') : 
                            if rec.pmvaction.realtime :
                                rec.pmvaction.redraw=False
                                #synchronize current structure with modeller
                                #updateMolAtomCoord(mol,mol.pmvaction.idConf,types=mol.pmvaction.sObject)
                                rec.pmvaction.updateModellerCoord(rec.pmvaction.idConf,rec.mdl)
                                #conjugate_gradients
                                rec.pmvaction.modellerOptimize(rec.pmvaction.mdstep,
                                                               rec.pmvaction.temp)                  
                else : 
                    for mol in mv.Mols:
                        print "ok ",mol
                        if hasattr(mol,'pmvaction') : 
                            print "pmvaction"
                            if mol.pmvaction.realtime :
                                print "lets modeller"
                                mol.pmvaction.redraw=False
                                #synchronize current structure with modeller
                                self.updateMolAtomCoord(mol,mol.pmvaction.idConf,
                                                        types=mol.pmvaction.sObject)
                                mol.pmvaction.updateModellerCoord(mol.pmvaction.idConf,mol.mdl)
                                #conjugate_gradients
                                mol.pmvaction.modellerOptimize(mol.pmvaction.mdstep,
                                                               mol.pmvaction.temp) #optimize and update coords
                

    def colorByEnergy(self,atomSet,scorer,property):
        mini = min(getattr(atomSet,scorer.prop))
        #geomsToColor = vf.getAvailableGeoms(scorer.mol2)
        self.mv.colorByProperty(atomSet,['cpk'],property,
                                mini=-1.0, maxi=1.0,
                                colormap='rgb256',log=1)#,

    def get_nrg_score(self,energy,display=True):
        #print "get_nrg_score"
        status = energy.compute_energies()
        print status
        if status is None: return
        print energy.current_scorer.score
        if hasattr(energy,'labels'):
            self.helper.updateText( energy.labels[0],
                    string="score :"+str(energy.current_scorer.score)[0:5])
            for i,term in enumerate(['el','hb','vw','so']):
                labelT = energy.labels[i+1]
                self.helper.updateText( labelT,
                string=term+" : "+str(energy.current_scorer.scores[i])[0:5])
        # change color of ligand with using scorer energy
        if energy.color[0] or energy.color[1] :
            # change selection level to Atom
            prev_select_level = self.mv.getSelLev()
            self.mv.setSelectionLevel(Atom,log=0)
            scorer = energy.current_scorer
            property = scorer.prop
            if energy.color[0] :
                atomSet1 = self.mv.expandNodes(scorer.mol1.name).findType(Atom) # we pick the rec
                if hasattr(atomSet1,scorer.prop):
                    self.colorByEnergy(atomSet1,scorer,property)
            if energy.color[1] :
                atomSet2 = self.mv.expandNodes(scorer.mol2.name).findType(Atom) # we pick the ligand
                if hasattr(atomSet2,scorer.prop):
                    self.colorByEnergy(atomSet2,scorer,property)
