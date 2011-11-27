Name:           testng
Version:        5.11
Release:        6
Summary:        Java-based testing framework

Group:          Development/Java
License:        ASL 2.0
URL:            http://testng.org/
Source0:        http://testng.org/%{name}-%{version}.zip
Source1:        http://repo2.maven.org/maven2/org/testng/testng/%{version}/testng-%{version}.pom
Patch0:         0001-Do-not-bundle-prebuilt-jar-s.patch
Patch1:         0001-Disable-DTDDoc-target.patch
Patch2:         0001-Port-to-QDoc-1.9.patch

BuildRoot:      %(mktemp -ud %{_tmppath}/%{name}-%{version}-%{release}-XXXXXX)

BuildRequires:  ant
BuildRequires:  unzip
BuildRequires:  jpackage-utils
BuildRequires:  java-devel-openjdk
BuildRequires:  bsh
BuildRequires:  qdox
BuildRequires:  junit
Requires:       jpackage-utils

BuildArch:      noarch

%description
TestNG is a testing framework inspired from JUnit and NUnit but introducing
some new functionality, including flexible test configuration, and
distributed test running.  It is designed to cover unit tests as well as
functional, end-to-end, integration, etc.


%package javadoc
Summary:        API Documentation for %{name}
Group:          Development/Java
Requires:       jpackage-utils

%description javadoc
JavaDoc documentation for %{name}


%prep
%setup -q
%patch0 -p1 -b .nobundle
%patch1 -p1 -b .dtddoc
%patch2 -p1 -b .qdoc19


%build
find -name '*.jar' -delete
CLASSPATH=$(build-classpath bsh qdox junit) \
        ant dist-15 javadocs

# Convert CP/M line encoding to UNIX one
sed 's/\r//' <README >README.unix
touch -r README README.unix
mv README.unix README


%install
rm -rf $RPM_BUILD_ROOT

# Code
install -d $RPM_BUILD_ROOT%{_javadir}
install -pm644 %{name}-%{version}-jdk15.jar \
        $RPM_BUILD_ROOT%{_javadir}/%{name}-%{version}.jar
ln -s %{name}-%{version}.jar \
        $RPM_BUILD_ROOT%{_javadir}/%{name}.jar

# API documentation
install -d $RPM_BUILD_ROOT%{_javadocdir}/%{name}-%{version}
cp -a javadocs/* $RPM_BUILD_ROOT%{_javadocdir}/%{name}-%{version}

# Maven stuff
install -d -m 755 $RPM_BUILD_ROOT%{_datadir}/maven2/poms
install -pm 644 %{SOURCE1} \
        $RPM_BUILD_ROOT/%{_datadir}/maven2/poms/JPP-%{name}.pom
%add_to_maven_depmap org.%{name} %{name} %{version} JPP %{name}


%clean
rm -rf $RPM_BUILD_ROOT


%files
%defattr(-,root,root,-)
%{_javadir}/*
%{_sysconfdir}/maven/fragments
%{_datadir}/maven2
%doc CHANGES.txt README LICENSE.txt


%files javadoc
%defattr(-,root,root,-)
%{_javadocdir}/*


%post
%update_maven_depmap


%postun
%update_maven_depmap


