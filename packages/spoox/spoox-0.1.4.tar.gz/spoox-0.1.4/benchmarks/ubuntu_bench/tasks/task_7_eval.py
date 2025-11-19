import subprocess
import sys
from pathlib import Path

if __name__ == "__main__":

    home = Path("/home/linus")
    project_test_dir = home / "jf_program" / "src" / "test" / "java"
    benchmark_dir = Path("/opt")

    # test if tests were modified
    if (
            not (benchmark_dir / "task_7_setup_FileSystemTest.java").open().read() == (
                    project_test_dir / "FileSystemTest.java").open().read()
            or not (benchmark_dir / "task_7_setup_DirectoryTest.java").open().read() == (
            project_test_dir / "DirectoryTest.java").open().read()
            or not (benchmark_dir / "task_7_setup_FileTest.java").open().read() == (
            project_test_dir / "FileTest.java").open().read()
            or not (benchmark_dir / "task_7_setup_ExceptionTest.java").open().read() == (
            project_test_dir / "ExceptionTest.java").open().read()
    ):
        sys.exit("Tests were modified, which is forbidden.")

    # check if httpie can be executed globally
    try:
        result_mvn_test = subprocess.run("cd /home/linus/jf_program && mvn test", shell=True, capture_output=True, text=True, user='linus')
        if result_mvn_test.returncode != 0:
            sys.exit("Executing the tests with mvn test failed.")
        if ('BUILD SUCCESS' not in result_mvn_test.stdout
                or 'ExceptionTest' not in result_mvn_test.stdout
                or 'FileSystemTest' not in result_mvn_test.stdout
                or 'FileTest' not in result_mvn_test.stdout
                or 'DirectoryTest' not in result_mvn_test.stdout):
            sys.exit("Maven reports test failures, errors or tests are skipped.")

    except Exception as e:
        sys.exit("Executing the tests did not work.")

    sys.exit(0)
