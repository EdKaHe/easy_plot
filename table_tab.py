# -*- coding: utf-8 -*-
"""
Created on Tue Nov 28 22:37:15 2017

@author: Ediz
"""

#create editable table widget
table_columns = [TableColumn(field=column, title=column) for column in columns]
table = DataTable(source=source_table, columns=table_columns, editable=True, width=1200, height=800)

#create layout of table tab
layout_table=layout([table])