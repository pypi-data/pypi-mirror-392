"""
依赖常量定义模块
定义不同包管理器下编译OpenSSH所需的依赖包
"""

# 编译OpenSSH所需的基本依赖包定义
REQUIRED_DEPENDENCIES = {
    'apt': [
        'build-essential',  # 基础编译工具
        'libssl-dev',       # OpenSSL开发库
        'openssl',          # OpenSSL库
        'zlib1g-dev',       # zlib压缩库开发文件
        'make',             # make工具
        'gcc',              # GCC编译器
        'g++',              # G++编译器
        'clang',            # Clang编译器（可选）
        'autoconf',         # 自动配置工具
        'automake',         # 自动构建工具
        'libtool',          # 库工具
        'pkg-config',       # pkg-config工具
        'curl',             # 下载工具
        'wget',             # 下载工具
        'tar',              # 解压工具
        'gzip',             # 压缩工具
    ],
    'yum': [
        'gcc',              # GCC编译器
        'gcc-c++',          # G++编译器
        'make',             # make工具
        'openssl-devel',    # OpenSSL开发库
        'openssl',          # OpenSSL库
        'openssl-libs',     # OpenSSL库文件（麒麟系统需要）
        'zlib-devel',       # zlib开发库
        'zlib',             # zlib库
        'clang',            # Clang编译器（可选）
        'autoconf',         # 自动配置工具
        'automake',         # 自动构建工具
        'libtool',          # 库工具
        'pkgconfig',        # pkg-config工具
        'curl',             # 下载工具
        'wget',             # 下载工具
        'tar',              # 解压工具
        'gzip',             # 压缩工具
        'krb5-devel',       # Kerberos开发库（OpenSSH可能需要）
        'libcap-devel',     # 功能强大的进程权限控制库
        'libselinux-devel', # SELinux开发库（某些系统需要）
        'pam-devel',        # PAM认证开发库（OpenSSH常用）
    ],
    'dnf': [
        'gcc',              # GCC编译器
        'gcc-c++',          # G++编译器
        'make',             # make工具
        'openssl-devel',    # OpenSSL开发库
        'openssl',          # OpenSSL库
        'zlib-devel',       # zlib开发库
        'clang',            # Clang编译器（可选）
        'autoconf',         # 自动配置工具
        'automake',         # 自动构建工具
        'libtool',          # 库工具
        'pkgconfig',        # pkg-config工具
        'curl',             # 下载工具
        'wget',             # 下载工具
        'tar',              # 解压工具
        'gzip',             # 压缩工具
    ],
    'zypper': [
        'gcc',              # GCC编译器
        'gcc-c++',          # G++编译器
        'make',             # make工具
        'libopenssl-devel', # OpenSSL开发库
        'libopenssl1_1',    # OpenSSL库
        'zlib-devel',       # zlib开发库
        'clang',            # Clang编译器（可选）
        'autoconf',         # 自动配置工具
        'automake',         # 自动构建工具
        'libtool',          # 库工具
        'pkg-config',       # pkg-config工具
        'curl',             # 下载工具
        'wget',             # 下载工具
        'tar',              # 解压工具
        'gzip',             # 压缩工具
    ],
    'pacman': [
        'base-devel',       # 基础开发工具
        'openssl',          # OpenSSL
        'zlib',             # zlib库
        'make',             # make工具
        'gcc',              # GCC编译器
        'clang',            # Clang编译器（可选）
        'autoconf',         # 自动配置工具
        'automake',         # 自动构建工具
        'libtool',          # 库工具
        'pkg-config',       # pkg-config工具
        'curl',             # 下载工具
        'wget',             # 下载工具
        'tar',              # 解压工具
        'gzip',             # 压缩工具
    ],
    'apk': [
        'build-base',       # 基础编译工具
        'openssl-dev',      # OpenSSL开发库
        'openssl',          # OpenSSL库
        'zlib-dev',         # zlib开发库
        'make',             # make工具
        'gcc',              # GCC编译器
        'g++',              # G++编译器
        'clang',            # Clang编译器（可选）
        'autoconf',         # 自动配置工具
        'automake',         # 自动构建工具
        'libtool',          # 库工具
        'pkgconf',          # pkg-config工具
        'curl',             # 下载工具
        'wget',             # 下载工具
        'tar',              # 解压工具
        'gzip',             # 压缩工具
    ]
}

# 包管理器检测列表
PACKAGE_MANAGERS = ['apt', 'yum', 'dnf', 'zypper', 'pacman', 'apk']

# 包管理器更新命令
PACKAGE_MANAGER_UPDATE_COMMANDS = {
    'apt': ['apt', 'update'],
    'yum': ['yum', 'makecache'],
    'dnf': ['dnf', 'makecache'],
    'zypper': ['zypper', 'refresh'],
    'pacman': ['pacman', '-Sy'],
    'apk': ['apk', 'update']
}

# 包管理器安装命令
PACKAGE_MANAGER_INSTALL_COMMANDS = {
    'apt': ['apt', 'install', '-y'],
    'yum': ['yum', 'install', '-y'],
    'dnf': ['dnf', 'install', '-y'],
    'zypper': ['zypper', 'install', '-y'],
    'pacman': ['pacman', '-S', '--noconfirm'],
    'apk': ['apk', 'add', '--no-cache']
}

# 依赖包描述信息
DEPENDENCY_DESCRIPTIONS = {
    'build-essential': '基础编译工具集',
    'libssl-dev': 'OpenSSL开发库',
    'openssl': 'OpenSSL库',
    'zlib1g-dev': 'zlib压缩库开发文件',
    'make': 'make构建工具',
    'gcc': 'GCC编译器',
    'g++': 'G++编译器',
    'clang': 'Clang编译器',
    'autoconf': '自动配置工具',
    'automake': '自动构建工具',
    'libtool': '库工具',
    'pkg-config': 'pkg-config工具',
    'curl': '下载工具',
    'wget': '下载工具',
    'tar': '解压工具',
    'gzip': '压缩工具',
    'openssl-devel': 'OpenSSL开发库',
    'zlib-devel': 'zlib开发库',
    'pkgconfig': 'pkg-config工具',
    'libopenssl-devel': 'OpenSSL开发库',
    'libopenssl1_1': 'OpenSSL 1.1库',
    'base-devel': '基础开发工具集',
    'zlib': 'zlib库',
    'build-base': '基础编译工具集',
    'openssl-dev': 'OpenSSL开发库',
    'zlib-dev': 'zlib开发库',
    'pkgconf': 'pkg-config工具',
    'openssl-libs': 'OpenSSL库文件',
    'krb5-devel': 'Kerberos开发库',
    'libcap-devel': '进程权限控制库',
    'libselinux-devel': 'SELinux开发库',
    'pam-devel': 'PAM认证开发库'
}