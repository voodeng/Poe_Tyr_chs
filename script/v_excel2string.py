# -*- coding: utf-8 -*-
import sys
import os
import pandas as pd
import numpy as np
import xml.etree.ElementTree as ET
import xlrd
import openpyxl
import datetime

from config import *
from lib import *

CUS = 'vmod'

excel_filename = os.path.join(TEMP_DIR, 'Tyranny_string_result.xlsx')

out_path_dir = os.path.join(TEMP_DIR, Cus)
''''
.stringtable 文件格式
<?xml version="1.0" encoding="UTF-8"?>
<StringTableFile xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema">
	<Name>game\edicts</Name>
	<NextEntryID>1</NextEntryID>
	<EntryCount>24</EntryCount>
	<Entries>
		<Entry>
			<ID>3</ID>
			<DefaultText>这道[url=glossary:edict]敕令[/url]会以猛烈的风暴轰击大地。在[url=glossary:edict]敕令[/url]维持期间，敌人会一直受到削弱。</DefaultText>
			<FemaleText/>
		</Entry>
    </Entries>
</StringTableFile>
''''