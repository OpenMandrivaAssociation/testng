# Copyright (c) 2000-2008, JPackage Project
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
# 1. Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the
#    distribution.
# 3. Neither the name of the JPackage Project nor the names of its
#    contributors may be used to endorse or promote products derived
#    from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
%define _with_gcj_support 1
%define gcj_support %{?_with_gcj_support:1}%{!?_with_gcj_support:%{?_without_gcj_support:0}%{!?_without_gcj_support:%{?_gcj_support:%{_gcj_support}}%{!?_gcj_support:0}}}

%define section free

Name:           testng
Version:        5.6
Release:        %mkrel 0.0.1
Epoch:          0
Summary:        TestNG
License:        Apache Software License 
Url:            http://testng.org
Source0:        http://testng.org/testng-5.6.zip
Source1:        testng-test.tar.gz
# svn export http://testng.googlecode.com/svn/trunk/test/
Source2:        testng-test-14.tar.gz
# svn export http://testng.googlecode.com/svn/trunk/test-14/
Source3:        %{name}-%{version}.pom

Patch0:         testng-test-BaseTest.patch
Patch1:         testng-test-v4-BaseTest.patch
Patch2:         testng-test-14-BaseTest.patch
Patch3:         testng-test-14-v4-BaseTest.patch

Group:          Development/Java
BuildRequires:  jpackage-utils >= 0:1.7.4
BuildRequires:  java-rpmbuild >= 0:1.5.0
BuildRequires:  ant >= 0:1.6.5
BuildRequires:  ant-junit
BuildRequires:  junit
BuildRequires:  bsh
BuildRequires:  qdox
BuildRequires:  xalan-j2
%if ! %{gcj_support}
BuildArch:      noarch
%endif
BuildRoot: %{_tmppath}/%{name}-%{version}-buildroot
%if %{gcj_support}
BuildRequires:    java-gcj-compat-devel
%endif
Requires:  bsh
Requires:  qdox

%description
TestNG is a testing framework inspired from JUnit and NUnit
but introducing some new functionalities that make it more 
powerful and easier to use, such as:
- JDK 5 Annotations (JDK 1.4 is also supported with JavaDoc 
  annotations). 
- Flexible test configuration. 
- Support for data-driven testing (with @DataProvider). 
- Support for parameters. 
- Allows distribution of tests on slave machines. 
- Powerful execution model (no more TestSuite). 
- Supported by a variety of tools and plug-ins (Eclipse, 
  IDEA, Maven, etc...). 
- Embeds BeanShell for further flexibility. 
- Default JDK functions for runtime and logging 
  (no dependencies). 
- Dependent methods for application server testing. 
TestNG is designed to cover all categories of tests:  
unit, functional, end-to-end, integration, etc...



%package javadoc
Summary:        Javadoc for %{name}
Group:          Development/Java

%description javadoc
%{summary}.

%package manual
Summary:        Documents for %{name}
Group:          Development/Java

%description manual
%{summary}.

%prep
%setup -q -c
gzip -dc %{SOURCE1} | tar xf -
gzip -dc %{SOURCE2} | tar xf -
rm test/src/test/invocationcount/DataProviderFalseFalseTest.java
rm test/src/test/invocationcount/DataProviderFalseTrueTest.java
rm test/src/test/invocationcount/DataProviderTrueFalseTest.java
rm test/src/test/invocationcount/DataProviderTrueTrueTest.java
rm test/src/test/invocationcount/FailedInvocationCountTest.java
rm test/src/test/invocationcount/FailedInvocationCount2.java
rm test/src/test/invocationcount/FirstAndLastTimeTest.java
rm test/src/test/invocationcount/InvocationCountFalseFalseTest.java
rm test/src/test/invocationcount/InvocationCountFalseTrueTest.java
rm test/src/test/invocationcount/InvocationCountTrueFalseTest.java
rm test/src/test/invocationcount/InvocationCountTrueTrueTest.java
%remove_java_binaries

ln -sf $(build-classpath bsh) 3rdparty/bsh-2.0b4.jar
ln -sf $(build-classpath qdox) 3rdparty/qdox-1.6.1.jar
ln -sf $(build-classpath junit) 3rdparty/junit.jar

%patch0 -b .sav0
%patch1 -b .sav1
%patch2 -b .sav2
%patch3 -b .sav3

%build
export JAVA_HOME=%{_jvmdir}/java-1.5.0
export CLASSPATH=$(build-classpath xalan-j2-serializer bsh)
%{ant} dist-15 javadocs

%install
rm -rf $RPM_BUILD_ROOT
# jars
install -d -m 755 $RPM_BUILD_ROOT%{_javadir}

install -m 644 %{name}-%{version}-jdk15.jar $RPM_BUILD_ROOT%{_javadir}/%{name}-jdk15-%{version}.jar
%add_to_maven_depmap org.testng %{name}-jdk15 %{version} JPP %{name}-jdk15
%add_to_maven_depmap org.testng %{name} %{version} JPP %{name}-jdk15

(cd $RPM_BUILD_ROOT%{_javadir} 
for jar in *-%{version}*.jar; do ln -sf ${jar} `echo $jar| sed  "s|-%{version}||g"`; done)

# poms
install -d -m 755 $RPM_BUILD_ROOT%{_datadir}/maven2/poms
install -pm 644 %{SOURCE3} \
    $RPM_BUILD_ROOT%{_datadir}/maven2/poms/JPP-%{name}.pom

# javadoc
install -d -m 755 $RPM_BUILD_ROOT%{_javadocdir}/%{name}-%{version}
cp -pr javadocs $RPM_BUILD_ROOT%{_javadocdir}/%{name}-%{version}
ln -s %{name}-%{version} $RPM_BUILD_ROOT%{_javadocdir}/%{name} 

install -d -m 755 $RPM_BUILD_ROOT%{_docdir}/%{name}-%{version}
cp -pr doc $RPM_BUILD_ROOT%{_docdir}/%{name}-%{version}
cp -p *.txt $RPM_BUILD_ROOT%{_docdir}/%{name}-%{version}

%if %{gcj_support}
%{_bindir}/aot-compile-rpm
%endif

%clean
rm -rf $RPM_BUILD_ROOT

%post
%update_maven_depmap
%if %{gcj_support}
%{update_gcjdb}
%endif

%postun
%update_maven_depmap
%if %{gcj_support}
%%{clean_gcjdb}
%endif

%files
%defattr(0644,root,root,0755)
%{_javadir}/%{name}*.jar
%{_datadir}/maven2/poms/*
%{_mavendepmapfragdir}
%if %{gcj_support}
%dir %attr(-,root,root) %{_libdir}/gcj/%{name}
%attr(-,root,root) %{_libdir}/gcj/%{name}/%{name}-*.jar.*
%endif

%files javadoc
%defattr(0644,root,root,0755)
%{_javadocdir}/%{name}-%{version}
%ghost %{_javadocdir}/%{name}

%files manual
%defattr(0644,root,root,0755)
%{_docdir}/%{name}-%{version}
