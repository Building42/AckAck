# AckAck
AckAck is a python script that automatically generates a plist based on the licenses in your Carthage, CocoaPods, or SwiftPackageManager folder. When you use the plists in your app, the licenses will show up in the Settings app.

![Settings example](http://i.imgur.com/V4JfPlC.png)

## Installation

Simply download the [ackack.py script](https://raw.githubusercontent.com/Building42/AckAck/master/ackack.py) and store it in your project root or in a subfolder (e.g. Scripts).

```sh
$ wget https://raw.githubusercontent.com/Building42/AckAck/master/ackack.py
$ chmod +x ackack.py
```

## Usage

1. Make sure that you have a Settings.bundle in your project (otherwise create one with Xcode)
2. Make sure that you ran Carthage or CocoaPods (you should have a Carthage/Checkouts or Pods folder)
3. Run the script: ```./ackack.py```
4. The script will automatically try to find the input and output folders
5. After the script is done, you will have a Acknowledgements.plist and a plist for every license found

```
Settings.bundle
├── Root.plist
├── Acknowledgements.plist
├── Acknowledgements
│   ├── Charts.plist
│   ├── HTTPParserC.plist
│   ├── Telegraph.plist
```

### Options

You can see the options and other help information by running `./ackack.py --help`.

### Integrate into your build

1. Open your project in Xcode
2. Click on your project and then Build Phases
3. Click the + to add a `New Run Script Phase`
4. Paste the following in the script field:

```sh
cd $SRCROOT
./ackack.py
```

### Using with Swift Package Manager
Things get a little trickier when using SPM because of how Xcode stores the packages. If you plan to integrate with Xcode, set your Run Script Build Phase like so:

```sh
DERIVED_DATA_CANDIDATE="${BUILD_ROOT}"
while ! [ -d "${DERIVED_DATA_CANDIDATE}/SourcePackages/checkouts" ]; do
  if [ "${DERIVED_DATA_CANDIDATE}" = / ]; then
    echo >&2 "error: Unable to locate SourcePackages directory from BUILD_ROOT: '${BUILD_ROOT}'"
    exit 1
  fi

  DERIVED_DATA_CANDIDATE="$(dirname "${DERIVED_DATA_CANDIDATE}")"
done


cd $SRCROOT
./ackack.py --spminput ${DERIVED_DATA_CANDIDATE}
```

Otherwise, you'll need to specify the `--spminput` argument when running AckAck. SPM contents (unless you've specified otherwise) are located in your app's derived data folder under `/SourcePackages/checkouts`. The path to that folder usually looks something like this:

    /Users/username/Library/Developer/Xcode/DerivedData/AppName-buildUUID/SourcePackages/checkouts
