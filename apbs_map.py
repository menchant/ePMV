from DejaVu.colorMap import ColorMap
cm = ColorMap(name='cmap')
cfg = {'mini': -9.7678934313589334, 'maxi': 9.7678934313589334, 'labels': None, 'ramp': [[1.0, 0.0, 0.0, 1.0], [1.0, 0.0060000000000000053, 0.0060000000000000053, 1.0], [1.0, 0.01100000000000001, 0.01100000000000001, 1.0], [1.0, 0.02300000000000002, 0.02300000000000002, 1.0], [1.0, 0.029000000000000026, 0.029000000000000026, 1.0], [1.0, 0.03400000000000003, 0.03400000000000003, 1.0], [1.0, 0.046000000000000041, 0.046000000000000041, 1.0], [1.0, 0.051000000000000045, 0.051000000000000045, 1.0], [1.0, 0.057000000000000051, 0.057000000000000051, 1.0], [1.0, 0.06899999999999995, 0.06899999999999995, 1.0], [1.0, 0.073999999999999955, 0.073999999999999955, 1.0], [1.0, 0.085999999999999965, 0.085999999999999965, 1.0], [1.0, 0.09099999999999997, 0.09099999999999997, 1.0], [1.0, 0.096999999999999975, 0.096999999999999975, 1.0], [1.0, 0.10899999999999999, 0.10899999999999999, 1.0], [1.0, 0.11399999999999999, 0.11399999999999999, 1.0], [1.0, 0.12, 0.12, 1.0], [1.0, 0.13100000000000001, 0.13100000000000001, 1.0], [1.0, 0.13700000000000001, 0.13700000000000001, 1.0], [1.0, 0.14300000000000002, 0.14300000000000002, 1.0], [1.0, 0.15400000000000003, 0.15400000000000003, 1.0], [1.0, 0.16000000000000003, 0.16000000000000003, 1.0], [1.0, 0.17100000000000004, 0.17100000000000004, 1.0], [1.0, 0.17700000000000005, 0.17700000000000005, 1.0], [1.0, 0.18300000000000005, 0.18300000000000005, 1.0], [1.0, 0.19399999999999995, 0.19399999999999995, 1.0], [1.0, 0.19999999999999996, 0.19999999999999996, 1.0], [1.0, 0.20599999999999996, 0.20599999999999996, 1.0], [1.0, 0.21699999999999997, 0.21699999999999997, 1.0], [1.0, 0.22299999999999998, 0.22299999999999998, 1.0], [1.0, 0.23399999999999999, 0.23399999999999999, 1.0], [1.0, 0.23999999999999999, 0.23999999999999999, 1.0], [1.0, 0.246, 0.246, 1.0], [1.0, 0.25700000000000001, 0.25700000000000001, 1.0], [1.0, 0.26300000000000001, 0.26300000000000001, 1.0], [1.0, 0.26900000000000002, 0.26900000000000002, 1.0], [1.0, 0.28000000000000003, 0.28000000000000003, 1.0], [1.0, 0.28600000000000003, 0.28600000000000003, 1.0], [1.0, 0.29100000000000004, 0.29100000000000004, 1.0], [1.0, 0.30300000000000005, 0.30300000000000005, 1.0], [1.0, 0.30900000000000005, 0.30900000000000005, 1.0], [1.0, 0.31999999999999995, 0.31999999999999995, 1.0], [1.0, 0.32599999999999996, 0.32599999999999996, 1.0], [1.0, 0.33099999999999996, 0.33099999999999996, 1.0], [1.0, 0.34299999999999997, 0.34299999999999997, 1.0], [1.0, 0.34899999999999998, 0.34899999999999998, 1.0], [1.0, 0.35399999999999998, 0.35399999999999998, 1.0], [1.0, 0.36599999999999999, 0.36599999999999999, 1.0], [1.0, 0.371, 0.371, 1.0], [1.0, 0.377, 0.377, 1.0], [1.0, 0.38900000000000001, 0.38900000000000001, 1.0], [1.0, 0.39400000000000002, 0.39400000000000002, 1.0], [1.0, 0.40600000000000003, 0.40600000000000003, 1.0], [1.0, 0.41100000000000003, 0.41100000000000003, 1.0], [1.0, 0.41700000000000004, 0.41700000000000004, 1.0], [1.0, 0.42900000000000005, 0.42900000000000005, 1.0], [1.0, 0.43400000000000005, 0.43400000000000005, 1.0], [1.0, 0.43999999999999995, 0.43999999999999995, 1.0], [1.0, 0.45099999999999996, 0.45099999999999996, 1.0], [1.0, 0.45699999999999996, 0.45699999999999996, 1.0], [1.0, 0.46899999999999997, 0.46899999999999997, 1.0], [1.0, 0.47399999999999998, 0.47399999999999998, 1.0], [1.0, 0.47999999999999998, 0.47999999999999998, 1.0], [1.0, 0.49099999999999999, 0.49099999999999999, 1.0], [1.0, 0.497, 0.497, 1.0], [1.0, 0.503, 0.503, 1.0], [1.0, 0.51400000000000001, 0.51400000000000001, 1.0], [1.0, 0.52000000000000002, 0.52000000000000002, 1.0], [1.0, 0.52600000000000002, 0.52600000000000002, 1.0], [1.0, 0.53699999999999992, 0.53699999999999992, 1.0], [1.0, 0.54299999999999993, 0.54299999999999993, 1.0], [1.0, 0.55400000000000005, 0.55400000000000005, 1.0], [1.0, 0.56000000000000005, 0.56000000000000005, 1.0], [1.0, 0.56600000000000006, 0.56600000000000006, 1.0], [1.0, 0.57699999999999996, 0.57699999999999996, 1.0], [1.0, 0.58299999999999996, 0.58299999999999996, 1.0], [1.0, 0.58899999999999997, 0.58899999999999997, 1.0], [1.0, 0.59999999999999998, 0.59999999999999998, 1.0], [1.0, 0.60599999999999998, 0.60599999999999998, 1.0], [1.0, 0.61699999999999999, 0.61699999999999999, 1.0], [1.0, 0.623, 0.623, 1.0], [1.0, 0.629, 0.629, 1.0], [1.0, 0.64000000000000001, 0.64000000000000001, 1.0], [1.0, 0.64600000000000002, 0.64600000000000002, 1.0], [1.0, 0.65100000000000002, 0.65100000000000002, 1.0], [1.0, 0.66300000000000003, 0.66300000000000003, 1.0], [1.0, 0.66900000000000004, 0.66900000000000004, 1.0], [1.0, 0.67399999999999993, 0.67399999999999993, 1.0], [1.0, 0.68599999999999994, 0.68599999999999994, 1.0], [1.0, 0.69100000000000006, 0.69100000000000006, 1.0], [1.0, 0.70300000000000007, 0.70300000000000007, 1.0], [1.0, 0.70900000000000007, 0.70900000000000007, 1.0], [1.0, 0.71399999999999997, 0.71399999999999997, 1.0], [1.0, 0.72599999999999998, 0.72599999999999998, 1.0], [1.0, 0.73099999999999998, 0.73099999999999998, 1.0], [1.0, 0.73699999999999999, 0.73699999999999999, 1.0], [1.0, 0.749, 0.749, 1.0], [1.0, 0.754, 0.754, 1.0], [1.0, 0.76000000000000001, 0.76000000000000001, 1.0], [1.0, 0.77100000000000002, 0.77100000000000002, 1.0], [1.0, 0.77700000000000002, 0.77700000000000002, 1.0], [1.0, 0.78900000000000003, 0.78900000000000003, 1.0], [1.0, 0.79400000000000004, 0.79400000000000004, 1.0], [1.0, 0.80000000000000004, 0.80000000000000004, 1.0], [1.0, 0.81099999999999994, 0.81099999999999994, 1.0], [1.0, 0.81699999999999995, 0.81699999999999995, 1.0], [1.0, 0.82299999999999995, 0.82299999999999995, 1.0], [1.0, 0.83399999999999996, 0.83399999999999996, 1.0], [1.0, 0.83999999999999997, 0.83999999999999997, 1.0], [1.0, 0.85099999999999998, 0.85099999999999998, 1.0], [1.0, 0.85699999999999998, 0.85699999999999998, 1.0], [1.0, 0.86299999999999999, 0.86299999999999999, 1.0], [1.0, 0.874, 0.874, 1.0], [1.0, 0.88, 0.88, 1.0], [1.0, 0.88600000000000001, 0.88600000000000001, 1.0], [1.0, 0.89700000000000002, 0.89700000000000002, 1.0], [1.0, 0.90300000000000002, 0.90300000000000002, 1.0], [1.0, 0.90900000000000003, 0.90900000000000003, 1.0], [1.0, 0.92000000000000004, 0.92000000000000004, 1.0], [1.0, 0.92600000000000005, 0.92600000000000005, 1.0], [1.0, 0.93700000000000006, 0.93700000000000006, 1.0], [1.0, 0.94299999999999995, 0.94299999999999995, 1.0], [1.0, 0.94899999999999995, 0.94899999999999995, 1.0], [1.0, 0.95999999999999996, 0.95999999999999996, 1.0], [1.0, 0.96599999999999997, 0.96599999999999997, 1.0], [1.0, 0.97099999999999997, 0.97099999999999997, 1.0], [1.0, 0.98299999999999998, 0.98299999999999998, 1.0], [1.0, 0.98899999999999999, 0.98899999999999999, 1.0], [1.0, 1.0, 1.0, 1.0], [1.0, 1.0, 1.0, 1.0], [0.98902199999999996, 0.98899999999999999, 1.0, 1.0], [1.0, 1.0, 1.0, 1.0], [0.97105799999999998, 0.97099999999999997, 1.0, 1.0], [0.96606800000000004, 0.96599999999999997, 1.0, 1.0], [0.95409199999999994, 0.95399999999999996, 1.0, 1.0], [0.949102, 0.94899999999999995, 1.0, 1.0], [0.93712600000000013, 0.93700000000000006, 1.0, 1.0], [0.93113800000000013, 0.93100000000000005, 1.0, 1.0], [0.92614800000000008, 0.92600000000000005, 1.0, 1.0], [0.9141720000000001, 0.91400000000000003, 1.0, 1.0], [0.90918200000000005, 0.90900000000000003, 1.0, 1.0], [0.90319400000000005, 0.90300000000000002, 1.0, 1.0], [0.89121800000000007, 0.89100000000000001, 1.0, 1.0], [0.88622800000000013, 0.88600000000000001, 1.0, 1.0], [0.87425200000000003, 0.874, 1.0, 1.0], [0.86926200000000009, 0.86899999999999999, 1.0, 1.0], [0.8632740000000001, 0.86299999999999999, 1.0, 1.0], [0.85129800000000011, 0.85099999999999998, 1.0, 1.0], [0.84630800000000006, 0.84599999999999997, 1.0, 1.0], [0.84032000000000007, 0.83999999999999997, 1.0, 1.0], [0.82934200000000002, 0.82899999999999996, 1.0, 1.0], [0.82335400000000014, 0.82299999999999995, 1.0, 1.0], [0.81137800000000004, 0.81099999999999994, 1.0, 1.0], [0.80638800000000022, 0.80600000000000005, 1.0, 1.0], [0.80040000000000022, 0.80000000000000004, 1.0, 1.0], [0.78942200000000018, 0.78900000000000003, 1.0, 1.0], [0.78343400000000019, 0.78300000000000003, 1.0, 1.0], [0.77744600000000019, 0.77700000000000002, 1.0, 1.0], [0.76646800000000015, 0.76600000000000001, 1.0, 1.0], [0.76048000000000016, 0.76000000000000001, 1.0, 1.0], [0.74950200000000011, 0.749, 1.0, 1.0], [0.74351400000000023, 0.74299999999999999, 1.0, 1.0], [0.73752600000000013, 0.73699999999999999, 1.0, 1.0], [0.72654800000000019, 0.72599999999999998, 1.0, 1.0], [0.72056000000000009, 0.71999999999999997, 1.0, 1.0], [0.71457200000000021, 0.71399999999999997, 1.0, 1.0], [0.70359400000000027, 0.70300000000000007, 1.0, 1.0], [0.69760600000000028, 0.69700000000000006, 1.0, 1.0], [0.68662800000000013, 0.68599999999999994, 1.0, 1.0], [0.68064000000000013, 0.67999999999999994, 1.0, 1.0], [0.67465200000000014, 0.67399999999999993, 1.0, 1.0], [0.66367400000000032, 0.66300000000000003, 1.0, 1.0], [0.65768600000000021, 0.65700000000000003, 1.0, 1.0], [0.64670800000000028, 0.64600000000000002, 1.0, 1.0], [0.64072000000000018, 0.64000000000000001, 1.0, 1.0], [0.6347320000000003, 0.63400000000000001, 1.0, 1.0], [0.62375400000000025, 0.623, 1.0, 1.0], [0.61776600000000026, 0.61699999999999999, 1.0, 1.0], [0.61177800000000027, 0.61099999999999999, 1.0, 1.0], [0.60080000000000022, 0.59999999999999998, 1.0, 1.0], [0.59481200000000023, 0.59399999999999997, 1.0, 1.0], [0.58383400000000019, 0.58299999999999996, 1.0, 1.0], [0.5778460000000003, 0.57699999999999996, 1.0, 1.0], [0.5718580000000002, 0.57099999999999995, 1.0, 1.0], [0.56088000000000027, 0.56000000000000005, 1.0, 1.0], [0.55489200000000038, 0.55400000000000005, 1.0, 1.0], [0.54990200000000022, 0.54899999999999993, 1.0, 1.0], [0.53792600000000024, 0.53699999999999992, 1.0, 1.0], [0.53193800000000035, 0.53100000000000003, 1.0, 1.0], [0.52096000000000031, 0.52000000000000002, 1.0, 1.0], [0.51497200000000032, 0.51400000000000001, 1.0, 1.0], [0.50998200000000038, 0.50900000000000001, 1.0, 1.0], [0.49800600000000028, 0.497, 1.0, 1.0], [0.49201800000000029, 0.49099999999999999, 1.0, 1.0], [0.48702800000000035, 0.48599999999999999, 1.0, 1.0], [0.47505200000000036, 0.47399999999999998, 1.0, 1.0], [0.47006200000000031, 0.46899999999999997, 1.0, 1.0], [0.45808600000000033, 0.45699999999999996, 1.0, 1.0], [0.45209800000000033, 0.45099999999999996, 1.0, 1.0], [0.44710800000000028, 0.44599999999999995, 1.0, 1.0], [0.43513200000000041, 0.43400000000000005, 1.0, 1.0], [0.43014200000000047, 0.42900000000000005, 1.0, 1.0], [0.42415400000000048, 0.42300000000000004, 1.0, 1.0], [0.41217800000000038, 0.41100000000000003, 1.0, 1.0], [0.40718800000000044, 0.40600000000000003, 1.0, 1.0], [0.39521200000000045, 0.39400000000000002, 1.0, 1.0], [0.3902220000000004, 0.38900000000000001, 1.0, 1.0], [0.38423400000000041, 0.38300000000000001, 1.0, 1.0], [0.37225800000000042, 0.371, 1.0, 1.0], [0.36726800000000037, 0.36599999999999999, 1.0, 1.0], [0.36128000000000038, 0.35999999999999999, 1.0, 1.0], [0.35030200000000045, 0.34899999999999998, 1.0, 1.0], [0.34431400000000045, 0.34299999999999997, 1.0, 1.0], [0.33233800000000036, 0.33099999999999996, 1.0, 1.0], [0.32734800000000042, 0.32599999999999996, 1.0, 1.0], [0.32136000000000042, 0.31999999999999995, 1.0, 1.0], [0.31038200000000049, 0.30900000000000005, 1.0, 1.0], [0.3043940000000005, 0.30300000000000005, 1.0, 1.0], [0.29241800000000051, 0.29100000000000004, 1.0, 1.0], [0.28742800000000046, 0.28600000000000003, 1.0, 1.0], [0.28144000000000047, 0.28000000000000003, 1.0, 1.0], [0.27046200000000054, 0.26900000000000002, 1.0, 1.0], [0.26447400000000054, 0.26300000000000001, 1.0, 1.0], [0.25848600000000055, 0.25700000000000001, 1.0, 1.0], [0.24750800000000051, 0.246, 1.0, 1.0], [0.24152000000000051, 0.23999999999999999, 1.0, 1.0], [0.23054200000000047, 0.22899999999999998, 1.0, 1.0], [0.22455400000000048, 0.22299999999999998, 1.0, 1.0], [0.21856600000000048, 0.21699999999999997, 1.0, 1.0], [0.20758800000000044, 0.20599999999999996, 1.0, 1.0], [0.20160000000000045, 0.19999999999999996, 1.0, 1.0], [0.19561200000000045, 0.19399999999999995, 1.0, 1.0], [0.18463400000000063, 0.18300000000000005, 1.0, 1.0], [0.17864600000000064, 0.17700000000000005, 1.0, 1.0], [0.16766800000000059, 0.16600000000000004, 1.0, 1.0], [0.1616800000000006, 0.16000000000000003, 1.0, 1.0], [0.15569200000000061, 0.15400000000000003, 1.0, 1.0], [0.14471400000000056, 0.14300000000000002, 1.0, 1.0], [0.13872600000000057, 0.13700000000000001, 1.0, 1.0], [0.13273800000000058, 0.13100000000000001, 1.0, 1.0], [0.12176000000000053, 0.12, 1.0, 1.0], [0.11577200000000054, 0.11399999999999999, 1.0, 1.0], [0.10479400000000061, 0.10299999999999998, 1.0, 1.0], [0.098806000000000616, 0.096999999999999975, 1.0, 1.0], [0.092818000000000622, 0.09099999999999997, 1.0, 1.0], [0.081840000000000579, 0.07999999999999996, 1.0, 1.0], [0.075852000000000586, 0.073999999999999955, 1.0, 1.0], [0.070862000000000536, 0.06899999999999995, 1.0, 1.0], [0.05888600000000066, 0.057000000000000051, 1.0, 1.0], [0.052898000000000667, 0.051000000000000045, 1.0, 1.0], [0.041920000000000623, 0.040000000000000036, 1.0, 1.0], [0.03593200000000063, 0.03400000000000003, 1.0, 1.0], [0.030942000000000691, 0.029000000000000026, 1.0, 1.0], [0.018966000000000705, 0.017000000000000015, 1.0, 1.0], [0.012978000000000711, 0.01100000000000001, 1.0, 1.0], [0.0020000000000006679, 0.0, 1.0, 1.0]], 'name': 'cmap'}
cm.configure(*(), **cfg)
