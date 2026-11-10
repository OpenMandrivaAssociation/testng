Name:		testng
Version:	6.3.1
Release:	1
Summary:	Testing framework for Java
Group:		Development/Java
License:	Apache-2.0 and CPL
URL:		https://testng.org/
Source0:	https://github.com/cbeust/testng/archive/refs/tags/testng-%{version}.tar.gz#/testng-%{version}.tar.gz
Patch0:		testng-6.3.1-snakeyaml2-jcommander2.patch

BuildArch:	noarch
BuildRequires:	java-current-devel
BuildRequires:	sysjar
BuildRequires:	mvn(com.beust:jcommander)
BuildRequires:	mvn(com.google.inject:guice)
BuildRequires:	mvn(junit:junit)
BuildRequires:	mvn(org.apache.ant:ant)
BuildRequires:	mvn(org.apache-extras.beanshell:bsh)
BuildRequires:	mvn(org.yaml:snakeyaml)

%description
TestNG 6.3.1 is the release Gradle 8.11.1 strictly pins. Later releases
break Gradle's cross-version test filtering, and TestNG 7.6 needs
Java 11. This package builds that release from source. SnakeYAML 2
removed Loader, so suite YAML is loaded through Constructor and
LoaderOptions. JCommander 2 splits comma-separated method lists with
CommaParameterSplitter. Vendored jars are not in the archive.
AbstractRemoteTestRunnerClient is Common Public License 1.0. The rest
is Apache-2.0.

%prep
%autosetup -n testng-%{version} -p1
find . -name '*.jar' -delete
find . -name '*.class' -delete

%build
export JAVA_HOME=%{_jvmdir}/java-openjdk
export PATH=$JAVA_HOME/bin:$PATH
mkdir -p classes
find src/main/java -name '*.java' > sources.list
javac --release 8 -encoding UTF-8 -Xlint:-options -Xlint:-path \
	-cp "%{_javadir}/jcommander.jar:%{_javadir}/google-guice.jar:%{_javadir}/junit.jar:%{_javadir}/ant.jar:%{_javadir}/bsh.jar:%{_javadir}/snakeyaml.jar" \
	-d classes @sources.list
cp -a src/main/resources/. classes/
jar cf testng.jar -C classes .
cat > testng.pom <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0">
  <modelVersion>4.0.0</modelVersion>
  <groupId>org.testng</groupId>
  <artifactId>testng</artifactId>
  <version>%{version}</version>
  <name>TestNG</name>
  <description>Testing framework. Gradle 8.11.1 pins 6.3.1.</description>
  <url>https://testng.org/</url>
  <licenses>
    <license>
      <name>Apache-2.0</name>
      <url>https://www.apache.org/licenses/LICENSE-2.0.txt</url>
    </license>
  </licenses>
  <dependencies>
    <dependency>
      <groupId>com.beust</groupId>
      <artifactId>jcommander</artifactId>
      <version>2.0</version>
    </dependency>
    <dependency>
      <groupId>com.google.inject</groupId>
      <artifactId>guice</artifactId>
      <version>5.1.0</version>
    </dependency>
    <dependency>
      <groupId>junit</groupId>
      <artifactId>junit</artifactId>
      <version>4.13.2</version>
    </dependency>
    <dependency>
      <groupId>org.apache.ant</groupId>
      <artifactId>ant</artifactId>
      <version>1.10.18</version>
    </dependency>
    <dependency>
      <groupId>org.yaml</groupId>
      <artifactId>snakeyaml</artifactId>
      <version>2.7</version>
    </dependency>
  </dependencies>
</project>
EOF

%install
sysjar install --buildroot %{buildroot} \
	--artifact testng.pom:testng.jar \
	--file-name testng \
	--filelist .mfiles

%check
export JAVA_HOME=%{_jvmdir}/java-openjdk
export PATH=$JAVA_HOME/bin:$PATH
JAR=%{buildroot}%{_javadir}/testng.jar
test -f "$JAR"
mkdir -p check
cat > check/Smoke.java <<'END'
public class Smoke {
	public static void main(String[] args) {
		org.testng.xml.XmlTest test = new org.testng.xml.XmlTest();
		test.setName("gradle");
		if (org.testng.ITestResult.SUCCESS != 1) {
			throw new RuntimeException("status");
		}
		System.out.println("testng_ok " + test.getName());
	}
}
END
CP="$JAR:%{_javadir}/jcommander.jar:%{_javadir}/google-guice.jar:%{_javadir}/junit.jar:%{_javadir}/ant.jar:%{_javadir}/snakeyaml.jar"
javac --release 8 -encoding UTF-8 -Xlint:-options -cp "$CP" -d check check/Smoke.java
java -cp "check:$CP" Smoke > check/out.txt
grep -F 'testng_ok gradle' check/out.txt

%files -f .mfiles
%license LICENSE.txt
%doc README
