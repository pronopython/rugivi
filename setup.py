from setuptools import setup

setup(name='rugivi',
	version='0.2.0-alpha',
	description='RuGiVi - Adult Media Landscape Browser',
	url='https://github.com/pronopython/rugivi',
	author='pronopython',
	author_email='pronopython@proton.me',
	license='GNU GENERAL PUBLIC LICENSE V3',
	packages=['rugivi'],
	package_data={'rugivi':['*']},
	include_package_data=True,
	zip_safe=False,
	install_requires=['pygame','psutil','numpy','sqlitedict','pyshortcuts'],
	entry_points={
        'gui_scripts': [
            'rugivi_configurator=rugivi.rugivi_configurator:main'
		],
        'console_scripts': [
            'rugivi_printModuleDir=rugivi.print_module_dir:printModuleDir',
            'rugivi=rugivi.rugivi:main'
		]
    	}
    )

#print("the exit is here")

