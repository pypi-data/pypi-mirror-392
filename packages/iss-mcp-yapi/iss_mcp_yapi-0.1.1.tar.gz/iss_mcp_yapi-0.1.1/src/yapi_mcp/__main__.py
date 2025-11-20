from .server import mcp
import argparse
def main():
    parser = argparse.ArgumentParser(description="yapi mcp service")
    parser.parse_args()
    print("启动yapi mcp服务")
    mcp.run()


if __name__ == "__main__":
    main()