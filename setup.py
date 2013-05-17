# this grabs the requirements from requirements.txt
REQUIREMENTS = [i.strip() for i in open("requirements/common.txt").readlines()]

setup(
    install_requires=REQUIREMENTS
)